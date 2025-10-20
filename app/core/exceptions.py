from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FlinkManagerException(Exception):
    """Exception cơ bản cho Flink Manager"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class ArtifactNotFoundError(FlinkManagerException):
    """Artifact không tồn tại"""
    def __init__(self, artifact_id: str):
        super().__init__(
            message=f"Artifact với ID {artifact_id} không tồn tại",
            error_code="ARTIFACT_NOT_FOUND",
            details={"artifact_id": artifact_id}
        )


class JobConfigNotFoundError(FlinkManagerException):
    """Job config không tồn tại"""
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job config với ID {job_id} không tồn tại",
            error_code="JOB_CONFIG_NOT_FOUND",
            details={"job_id": job_id}
        )


class ArtifactVersionExistsError(FlinkManagerException):
    """Phiên bản artifact đã tồn tại"""
    def __init__(self, artifact_name: str, version: str):
        super().__init__(
            message=f"Artifact {artifact_name} phiên bản {version} đã tồn tại",
            error_code="ARTIFACT_VERSION_EXISTS",
            details={"artifact_name": artifact_name, "version": version}
        )


class JobNameExistsError(FlinkManagerException):
    """Tên job đã tồn tại"""
    def __init__(self, job_name: str):
        super().__init__(
            message=f"Job với tên {job_name} đã tồn tại",
            error_code="JOB_NAME_EXISTS",
            details={"job_name": job_name}
        )


class FlinkClusterError(FlinkManagerException):
    """Lỗi từ Flink cluster"""
    def __init__(self, message: str, flink_error: Optional[str] = None):
        super().__init__(
            message=f"Lỗi Flink cluster: {message}",
            error_code="FLINK_CLUSTER_ERROR",
            details={"flink_error": flink_error}
        )


class MinIOError(FlinkManagerException):
    """Lỗi MinIO"""
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=f"Lỗi MinIO: {message}",
            error_code="MINIO_ERROR",
            details={"operation": operation}
        )


def handle_exception(exc: Exception) -> HTTPException:
    """Xử lý exception và trả về HTTPException"""
    if isinstance(exc, FlinkManagerException):
        status_code = status.HTTP_400_BAD_REQUEST
        
        # Map specific errors to appropriate HTTP status codes
        if isinstance(exc, (ArtifactNotFoundError, JobConfigNotFoundError)):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, (ArtifactVersionExistsError, JobNameExistsError)):
            status_code = status.HTTP_409_CONFLICT
        elif isinstance(exc, (FlinkClusterError, MinIOError)):
            status_code = status.HTTP_502_BAD_GATEWAY
        
        return HTTPException(
            status_code=status_code,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details
            }
        )
    
    # Log unexpected errors
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": "Lỗi hệ thống không mong muốn",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

