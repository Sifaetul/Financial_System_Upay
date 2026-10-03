from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import custom_exception_handler
import time
import logging
import json
import uuid

app = FastAPI(title=settings.PROJECT_NAME)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("upay_nexus")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers_and_logging(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        # Structured Logging
        log_data = {
            "timestamp": time.time(),
            "level": "INFO",
            "service": "api",
            "environment": settings.ENVIRONMENT,
            "request_id": request_id,
            "method": request.method,
            "route": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms
        }
        logger.info(json.dumps(log_data))

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        log_data = {
            "timestamp": time.time(),
            "level": "ERROR",
            "service": "api",
            "environment": settings.ENVIRONMENT,
            "request_id": request_id,
            "method": request.method,
            "route": request.url.path,
            "error_type": type(exc).__name__,
            "duration_ms": duration_ms
        }
        logger.error(json.dumps(log_data))
        return custom_exception_handler(request, exc)

app.add_exception_handler(Exception, custom_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(json.dumps({"event": "shutdown", "service": "api"}))
