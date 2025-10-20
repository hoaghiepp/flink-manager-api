from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional

from app.services.job_spec_service import job_spec_service, execution_service
from app.schemas.job_config import (
    JobSpecCreate, JobSpecUpdate, JobSpecResponse, JobSpecListResponse,
    ExecutionCreate, ExecutionResponse, ExecutionListResponse,
    ExecutionStartResponse, ExecutionStopResponse, ExecutionHistoryResponse
)
from app.schemas.common import BaseResponse, PaginationParams
from app.core.exceptions import handle_exception
from app.models.job_config import JobStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/job-specs", tags=["Job Specifications"])


@router.post("/", response_model=BaseResponse, summary="Tạo Job Spec")
async def create_job_spec(job_spec_data: JobSpecCreate):
    """
    Tạo job specification mới
    
    - **job_spec_name**: Tên job spec (duy nhất)
    - **artifact_id**: ID của artifact
    - **entry_class**: Entry class để chạy
    - **parallelism**: Mức độ song song
    - **program_args**: Tham số chương trình
    - **flink_config**: Cấu hình Flink
    """
    try:
        job_spec_id = await job_spec_service.create_job_spec(job_spec_data)
        
        return BaseResponse(
            message="Tạo job spec thành công",
            data={"job_spec_id": job_spec_id}
        )
        
    except Exception as e:
        logger.error(f"Lỗi tạo job spec: {e}")
        raise handle_exception(e)


@router.get("/", response_model=BaseResponse, summary="Lấy danh sách Job Specs")
async def list_job_specs(
    page: int = Query(1, ge=1, description="Số trang"),
    size: int = Query(20, ge=1, le=100, description="Kích thước trang"),
    job_spec_name: Optional[str] = Query(None, description="Lọc theo tên job spec"),
    created_by: Optional[str] = Query(None, description="Lọc theo người tạo"),
    sort_by: str = Query("created_at", description="Trường sắp xếp"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp")
):
    """
    Lấy danh sách job specs với phân trang và lọc
    """
    try:
        job_specs, total = await job_spec_service.list_job_specs(
            page=page,
            size=size,
            job_spec_name=job_spec_name,
            created_by=created_by,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        job_spec_responses = []
        for job_spec in job_specs:
            job_spec_responses.append(JobSpecResponse(**job_spec.dict()))
        
        return BaseResponse(
            data={
                "job_specs": job_spec_responses,
                "total": total,
                "page": page,
                "size": size
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi lấy danh sách job specs: {e}")
        raise handle_exception(e)


@router.get("/{job_spec_id}", response_model=BaseResponse, summary="Lấy Job Spec theo ID")
async def get_job_spec(job_spec_id: str):
    """
    Lấy thông tin chi tiết của job spec theo ID
    """
    try:
        job_spec = await job_spec_service.get_job_spec(job_spec_id)
        if not job_spec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job spec với ID {job_spec_id} không tồn tại"
            )
        
        return BaseResponse(data=JobSpecResponse(**job_spec.dict()))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi lấy job spec: {e}")
        raise handle_exception(e)


@router.put("/{job_spec_id}", response_model=BaseResponse, summary="Cập nhật Job Spec")
async def update_job_spec(job_spec_id: str, update_data: JobSpecUpdate):
    """
    Cập nhật job specification
    """
    try:
        success = await job_spec_service.update_job_spec(job_spec_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job spec với ID {job_spec_id} không tồn tại"
            )
        
        return BaseResponse(message="Cập nhật job spec thành công")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi cập nhật job spec: {e}")
        raise handle_exception(e)


@router.delete("/{job_spec_id}", response_model=BaseResponse, summary="Xóa Job Spec")
async def delete_job_spec(job_spec_id: str):
    """
    Xóa job specification
    """
    try:
        success = await job_spec_service.delete_job_spec(job_spec_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job spec với ID {job_spec_id} không tồn tại"
            )
        
        return BaseResponse(message="Xóa job spec thành công")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi xóa job spec: {e}")
        raise handle_exception(e)


# Execution endpoints
@router.post("/{job_spec_id}/executions", response_model=BaseResponse, summary="Bắt đầu Execution")
async def start_execution(job_spec_id: str, execution_data: ExecutionCreate):
    """
    Bắt đầu execution từ job spec
    
    - **started_by**: Người bắt đầu execution
    """
    try:
        result = await execution_service.start_execution(job_spec_id, execution_data)
        
        return BaseResponse(
            message="Bắt đầu execution thành công",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Lỗi bắt đầu execution: {e}")
        raise handle_exception(e)


@router.get("/{job_spec_id}/executions", response_model=BaseResponse, summary="Lấy danh sách Executions")
async def list_executions(
    job_spec_id: str,
    page: int = Query(1, ge=1, description="Số trang"),
    size: int = Query(20, ge=1, le=100, description="Kích thước trang"),
    status: Optional[JobStatus] = Query(None, description="Lọc theo trạng thái"),
    started_by: Optional[str] = Query(None, description="Lọc theo người bắt đầu"),
    sort_by: str = Query("started_at", description="Trường sắp xếp"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp")
):
    """
    Lấy danh sách executions của job spec
    """
    try:
        executions, total = await execution_service.list_executions(
            page=page,
            size=size,
            job_spec_id=job_spec_id,
            status=status,
            started_by=started_by,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        execution_responses = []
        for execution in executions:
            execution_responses.append(ExecutionResponse(**execution.dict()))
        
        return BaseResponse(
            data={
                "executions": execution_responses,
                "total": total,
                "page": page,
                "size": size
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi lấy danh sách executions: {e}")
        raise handle_exception(e)


# Global execution endpoints
@router.get("/executions/{execution_id}", response_model=BaseResponse, summary="Lấy Execution theo ID")
async def get_execution(execution_id: str):
    """
    Lấy thông tin chi tiết của execution theo ID
    """
    try:
        execution = await execution_service.get_execution(execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution với ID {execution_id} không tồn tại"
            )
        
        return BaseResponse(data=ExecutionResponse(**execution.dict()))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi lấy execution: {e}")
        raise handle_exception(e)


@router.post("/executions/{execution_id}/stop", response_model=BaseResponse, summary="Dừng Execution")
async def stop_execution(execution_id: str, savepoint: bool = False, savepoint_path: Optional[str] = None):
    """
    Dừng execution
    
    - **savepoint**: Tạo savepoint trước khi dừng
    - **savepoint_path**: Đường dẫn savepoint
    """
    try:
        result = await execution_service.stop_execution(
            execution_id, 
            savepoint=savepoint,
            savepoint_path=savepoint_path
        )
        
        return BaseResponse(
            message="Dừng execution thành công",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Lỗi dừng execution: {e}")
        raise handle_exception(e)


@router.get("/executions/{execution_id}/history", response_model=BaseResponse, summary="Lấy lịch sử Execution")
async def get_execution_history(execution_id: str):
    """
    Lấy lịch sử thay đổi trạng thái của execution
    """
    try:
        history = await execution_service.get_execution_history(execution_id)
        
        history_responses = []
        for h in history:
            history_responses.append(ExecutionHistoryResponse(**h.dict()))
        
        return BaseResponse(
            data={
                "execution_id": execution_id,
                "history": history_responses,
                "total": len(history_responses)
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi lấy execution history: {e}")
        raise handle_exception(e)
