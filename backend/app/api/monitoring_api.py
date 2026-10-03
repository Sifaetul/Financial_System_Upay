from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.monitoring_service import MonitoringService
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring & Governance"])

@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    return MonitoringService.get_health(db)

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    return MonitoringService.get_dashboard_summary(db)

@router.post("/events")
def log_telemetry_event(name: str, metric_type: str, value: float, service: str, db: Session = Depends(get_db)):
    metric = MonitoringService.log_metric(db, name, metric_type, value, service)
    return {"status": "ok", "id": metric.id}

@router.post("/governance")
def log_governance_event(actor: str, entity_type: str, entity_id: str, action: str, reason: str = None, db: Session = Depends(get_db)):
    evt = MonitoringService.log_governance_event(db, actor, entity_type, entity_id, action, reason=reason)
    return {"status": "ok", "id": evt.id}

@router.post("/data-quality/check")
def trigger_dq_check(db: Session = Depends(get_db)):
    res = MonitoringService.run_data_quality_check(db)
    return {"status": "ok", "feature": res.feature, "dq_status": res.status}
