from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.job_spec import ExecutionStatus


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
    execution_name: str = Field(..., description="Tên execution", min_length=1, max_length=100)
    started_by: str = Field(..., description="Người start execution", min_length=1)


class ExecutionResponse(BaseModel):
    """Response execution"""
    id: str
    job_spec_id: str
    execution_name: str
    flink_job_id: Optional[str]
    status: ExecutionStatus
    started_by: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class ExecutionListResponse(BaseModel):
    """Response danh sách executions"""
    executions: List[ExecutionResponse]
    total: int
    page: int
    size: int


class ExecutionSubmitRequest(BaseModel):
    """Schema để submit execution"""
    started_by: str = Field(..., description="Người submit", min_length=1)


class ExecutionSubmitResponse(BaseModel):
    """Response submit execution"""
    execution_id: str
    job_spec_id: str
    flink_job_id: str
    status: ExecutionStatus
    started_at: datetime
    started_by: str


class ExecutionStopRequest(BaseModel):
    """Schema để stop execution"""
    savepoint: bool = Field(default=False, description="Tạo savepoint trước khi stop")
    savepoint_path: Optional[str] = Field(None, description="Đường dẫn savepoint")


class ExecutionStopResponse(BaseModel):
    """Response stop execution"""
    execution_id: str
    flink_job_id: str
    status: ExecutionStatus
    stopped_at: datetime
    savepoint_path: Optional[str]


class ExecutionRestartRequest(BaseModel):
    """Schema để restart execution"""
    started_by: str = Field(..., description="Người restart", min_length=1)


class ExecutionRestartResponse(BaseModel):
    """Response restart execution"""
    execution_id: str
    job_spec_id: str
    flink_job_id: str
    status: ExecutionStatus
    started_at: datetime
    started_by: str


class ExecutionHistoryResponse(BaseModel):
    """Response lịch sử execution"""
    id: str
    execution_id: str
    job_spec_id: str
    action: str
    performed_by: str
    performed_at: datetime
    status: ExecutionStatus
    flink_job_id: Optional[str]
    error_message: Optional[str]
