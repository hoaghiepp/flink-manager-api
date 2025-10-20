from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.job_config import JobStatus


class JobConfigCreate(BaseModel):
    """Schema để tạo job config"""
    job_name: str = Field(..., description="Tên job", min_length=1, max_length=100)
    artifact_id: str = Field(..., description="ID của artifact")
    entry_class: str = Field(..., description="Entry class để chạy", min_length=1)
    parallelism: int = Field(default=1, description="Mức độ song song", ge=1, le=100)
    program_args: Optional[List[str]] = Field(default=[], description="Tham số chương trình")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")
    flink_config: Optional[Dict[str, Any]] = Field(default={}, description="Cấu hình Flink")
    created_by: str = Field(..., description="Người tạo job", min_length=1)
    
    @validator('job_name')
    def validate_job_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Tên job chỉ được chứa chữ cái, số, gạch ngang và gạch dưới')
        return v


class JobConfigUpdate(BaseModel):
    """Schema để cập nhật job config"""
    job_name: Optional[str] = Field(None, description="Tên job", min_length=1, max_length=100)
    entry_class: Optional[str] = Field(None, description="Entry class để chạy", min_length=1)
    parallelism: Optional[int] = Field(None, description="Mức độ song song", ge=1, le=100)
    program_args: Optional[List[str]] = Field(None, description="Tham số chương trình")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")
    flink_config: Optional[Dict[str, Any]] = Field(None, description="Cấu hình Flink")


class JobConfigResponse(BaseModel):
    """Response job config"""
    id: str
    job_name: str
    artifact_id: str
    entry_class: str
    parallelism: int
    program_args: List[str]
    savepoint_path: Optional[str]
    flink_config: Dict[str, Any]
    status: JobStatus
    flink_job_id: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_deployed_at: Optional[datetime]


class JobConfigListResponse(BaseModel):
    """Response danh sách job configs"""
    jobs: List[JobConfigResponse]
    total: int
    page: int
    size: int


class JobDeployRequest(BaseModel):
    """Schema để deploy job"""
    deployed_by: str = Field(..., description="Người deploy", min_length=1)


class JobDeployResponse(BaseModel):
    """Response deploy job"""
    job_id: str
    flink_job_id: str
    status: JobStatus
    deployed_at: datetime
    deployed_by: str


class JobStopRequest(BaseModel):
    """Schema để stop job"""
    savepoint: bool = Field(default=False, description="Tạo savepoint trước khi stop")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")


class JobStopResponse(BaseModel):
    """Response stop job"""
    job_id: str
    flink_job_id: str
    status: JobStatus
    stopped_at: datetime
    savepoint_path: Optional[str]


class DeploymentHistoryResponse(BaseModel):
    """Response lịch sử deployment"""
    id: str
    job_id: str
    artifact_id: str
    deployed_by: str
    deployed_at: datetime
    status: JobStatus
    flink_job_id: Optional[str]
    error_message: Optional[str]

