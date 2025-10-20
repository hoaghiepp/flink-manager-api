from typing import Optional, Dict, Any
from pydantic import BaseModel


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
    page: int = 1
    size: int = 20
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # asc hoặc desc


class PaginatedResponse(BaseModel):
    """Response phân trang"""
    success: bool = True
    data: Any
    pagination: Dict[str, Any]

