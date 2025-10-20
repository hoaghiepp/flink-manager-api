from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.job_config import JobStatus


class JobSpecCreate(BaseModel):
    """Schema để tạo job spec"""
    job_spec_name: str = Field(..., description="Tên job spec", min_length=1, max_length=100)
    artifact_id: str = Field(..., description="ID của artifact")
    entry_class: str = Field(..., description="Entry class để chạy", min_length=1)
    parallelism: int = Field(default=1, description="Mức độ song song", ge=1, le=100)
    program_args: Optional[List[str]] = Field(default=[], description="Tham số chương trình")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")
    flink_config: Optional[Dict[str, Any]] = Field(default={}, description="Cấu hình Flink")
    created_by: str = Field(..., description="Người tạo job spec", min_length=1)
    
    @validator('job_spec_name')
    def validate_job_spec_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Tên job spec chỉ được chứa chữ cái, số, gạch ngang và gạch dưới')
        return v


class JobSpecUpdate(BaseModel):
    """Schema để cập nhật job spec"""
    job_spec_name: Optional[str] = Field(None, description="Tên job spec", min_length=1, max_length=100)
    entry_class: Optional[str] = Field(None, description="Entry class để chạy", min_length=1)
    parallelism: Optional[int] = Field(None, description="Mức độ song song", ge=1, le=100)
    program_args: Optional[List[str]] = Field(None, description="Tham số chương trình")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")
    flink_config: Optional[Dict[str, Any]] = Field(None, description="Cấu hình Flink")


class JobSpecResponse(BaseModel):
    """Response job spec"""
    id: str
    job_spec_name: str
    artifact_id: str
    entry_class: str
    parallelism: int
    program_args: List[str]
    savepoint_path: Optional[str]
    flink_config: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime


class JobSpecListResponse(BaseModel):
    """Response danh sách job specs"""
    job_specs: List[JobSpecResponse]
    total: int
    page: int
    size: int


class ExecutionCreate(BaseModel):
    """Schema để tạo execution"""
    job_spec_id: str = Field(..., description="ID của job spec")
    started_by: str = Field(..., description="Người bắt đầu execution", min_length=1)


class ExecutionResponse(BaseModel):
    """Response execution"""
    id: str
    job_spec_id: str
    flink_job_id: Optional[str]
    status: JobStatus
    started_by: str
    started_at: datetime
    finished_at: Optional[datetime]
    error_message: Optional[str]


class ExecutionListResponse(BaseModel):
    """Response danh sách executions"""
    executions: List[ExecutionResponse]
    total: int
    page: int
    size: int


class ExecutionStartResponse(BaseModel):
    """Response start execution"""
    execution_id: str
    flink_job_id: str
    status: JobStatus
    started_at: datetime
    started_by: str


class ExecutionStopResponse(BaseModel):
    """Response stop execution"""
    execution_id: str
    flink_job_id: str
    status: JobStatus
    stopped_at: datetime
    savepoint_path: Optional[str]


class ExecutionHistoryResponse(BaseModel):
    """Response lịch sử execution"""
    id: str
    execution_id: str
    performed_by: str
    performed_at: datetime
    action: str
    old_status: Optional[JobStatus]
    new_status: JobStatus
    details: Optional[Dict[str, Any]]