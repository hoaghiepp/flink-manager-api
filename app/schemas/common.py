from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Response cơ bản"""
    success: bool = True
    message: str = "Thành công"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Response lỗi"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Tham số phân trang"""
    page: int = Field(default=1, ge=1, description="Số trang")
    size: int = Field(default=20, ge=1, le=100, description="Kích thước trang")
    sort_by: Optional[str] = Field(None, description="Trường sắp xếp")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp")


class PaginatedResponse(BaseModel):
    """Response phân trang"""
    success: bool = True
    data: Any
    pagination: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Response health check"""
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

