from fastapi import APIRouter, Depends, Response
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import redis_client
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=dict)
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

@router.get("/liveness")
def liveness():
    return {"status": "alive"}

@router.get("/readiness")
def readiness(response: Response, db: Session = Depends(get_db)):
    health_status = {"status": "ok", "dependencies": {}}
    
    # Check Postgres
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health_status["dependencies"]["postgres"] = "HEALTHY"
    except Exception:
        health_status["dependencies"]["postgres"] = "DEGRADED"
        health_status["status"] = "degraded"

    # Check Redis
    if redis_client:
        try:
            redis_client.ping()
            health_status["dependencies"]["redis"] = "HEALTHY"
        except Exception:
            health_status["dependencies"]["redis"] = "DEGRADED"
            health_status["status"] = "degraded"
    else:
        health_status["dependencies"]["redis"] = "DEGRADED"
        health_status["status"] = "degraded"
        
    if health_status["status"] == "degraded":
        response.status_code = 503
        
    return health_status

