from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class JobStatus(str, Enum):
    """Trạng thái của job"""
    CREATED = "created"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELED = "canceled"
    SUSPENDED = "suspended"


class JobConfig(BaseModel):
    """Model cho Job Configuration"""
    id: Optional[str] = Field(None, alias="_id")
    job_name: str = Field(..., description="Tên job")
    artifact_id: str = Field(..., description="ID của artifact")
    entry_class: str = Field(..., description="Entry class để chạy")
    parallelism: int = Field(default=1, description="Mức độ song song")
    program_args: Optional[List[str]] = Field(default=[], description="Tham số chương trình")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")
    flink_config: Optional[Dict[str, Any]] = Field(default={}, description="Cấu hình Flink")
    status: JobStatus = Field(default=JobStatus.CREATED, description="Trạng thái job")
    flink_job_id: Optional[str] = Field(None, description="ID job trong Flink cluster")
    created_by: str = Field(..., description="Người tạo job")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_deployed_at: Optional[datetime] = Field(None, description="Lần deploy cuối")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeploymentHistory(BaseModel):
    """Lịch sử deployment"""
    id: Optional[str] = Field(None, alias="_id")
    job_id: str = Field(..., description="ID của job")
    artifact_id: str = Field(..., description="ID của artifact")
    deployed_by: str = Field(..., description="Người deploy")
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
    status: JobStatus = Field(..., description="Trạng thái deployment")
    flink_job_id: Optional[str] = Field(None, description="ID job trong Flink")
    error_message: Optional[str] = Field(None, description="Thông báo lỗi nếu có")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

