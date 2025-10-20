from fastapi import APIRouter, Depends
from datetime import datetime
from app.schemas.common import HealthCheckResponse
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("/", response_model=HealthCheckResponse, summary="Health Check")
async def health_check():
    """
    Kiểm tra trạng thái hệ thống và các service dependencies
    """
    services_status = {}
    
    # Kiểm tra MongoDB (mock mode)
    try:
        services_status["mongodb"] = "healthy (mock)"
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        services_status["mongodb"] = "unhealthy"
    
    # Kiểm tra MinIO (mock mode)
    try:
        services_status["minio"] = "healthy (mock)"
    except Exception as e:
        logger.error(f"MinIO health check failed: {e}")
        services_status["minio"] = "unhealthy"
    
    # Kiểm tra Flink Cluster (mock mode)
    try:
        services_status["flink_cluster"] = "healthy (mock)"
    except Exception as e:
        logger.error(f"Flink cluster health check failed: {e}")
        services_status["flink_cluster"] = "unhealthy"
    
    # Xác định trạng thái tổng thể
    overall_status = "healthy"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version=settings.app_version,
        services=services_status
    )


@router.get("/ready", summary="Readiness Check")
async def readiness_check():
    """
    Kiểm tra readiness của ứng dụng
    """
    try:
        from app.core.database import get_database
        db = get_database()
        await db.command("ping")
        
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e), "timestamp": datetime.utcnow().isoformat()}


@router.get("/live", summary="Liveness Check")
async def liveness_check():
    """
    Kiểm tra liveness của ứng dụng
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

