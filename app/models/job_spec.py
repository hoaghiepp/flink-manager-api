from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ExecutionStatus(str, Enum):
    """Trạng thái của execution"""
    CREATED = "created"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELED = "canceled"
    SUSPENDED = "suspended"


class JobSpec(BaseModel):
    """Model cho Job Specification"""
    id: Optional[str] = Field(None, alias="_id")
    job_spec_name: str = Field(..., description="Tên job spec")
    artifact_id: str = Field(..., description="ID của artifact")
    entry_class: str = Field(..., description="Entry class để chạy")
    parallelism: int = Field(default=1, description="Mức độ song song")
    program_args: Optional[List[str]] = Field(default=[], description="Tham số chương trình")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")
    flink_config: Optional[Dict[str, Any]] = Field(default={}, description="Cấu hình Flink")
    created_by: str = Field(..., description="Người tạo job spec")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Execution(BaseModel):
    """Model cho Execution (runtime instance của JobSpec)"""
    id: Optional[str] = Field(None, alias="_id")
    job_spec_id: str = Field(..., description="ID của job spec")
    execution_name: str = Field(..., description="Tên execution")
    flink_job_id: Optional[str] = Field(None, description="ID job trong Flink cluster")
    status: ExecutionStatus = Field(default=ExecutionStatus.CREATED, description="Trạng thái execution")
    started_by: str = Field(..., description="Người start execution")
    started_at: Optional[datetime] = Field(None, description="Thời gian start")
    finished_at: Optional[datetime] = Field(None, description="Thời gian finish")
    error_message: Optional[str] = Field(None, description="Thông báo lỗi nếu có")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExecutionHistory(BaseModel):
    """Lịch sử execution"""
    id: Optional[str] = Field(None, alias="_id")
    execution_id: str = Field(..., description="ID của execution")
    job_spec_id: str = Field(..., description="ID của job spec")
    action: str = Field(..., description="Hành động (start, stop, restart)")
    performed_by: str = Field(..., description="Người thực hiện")
    performed_at: datetime = Field(default_factory=datetime.utcnow)
    status: ExecutionStatus = Field(..., description="Trạng thái sau hành động")
    flink_job_id: Optional[str] = Field(None, description="ID job trong Flink")
    error_message: Optional[str] = Field(None, description="Thông báo lỗi nếu có")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
