from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional

from app.services.job_service import job_service
from app.schemas.job_config import (
    JobConfigCreate, JobConfigUpdate, JobConfigResponse, JobConfigListResponse,
    JobDeployRequest, JobDeployResponse, JobStopRequest, JobStopResponse,
    DeploymentHistoryResponse
)
from app.schemas.common import BaseResponse, PaginationParams
from app.core.exceptions import handle_exception
from app.models.job_config import JobStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Job Configs"])


@router.post("/", response_model=BaseResponse, summary="Tạo Job Config")
async def create_job_config(job_data: JobConfigCreate):
    """
    Tạo job configuration mới
    
    - **job_name**: Tên job (duy nhất)
    - **artifact_id**: ID của artifact
    - **entry_class**: Entry class để chạy
    - **parallelism**: Mức độ song song
    - **program_args**: Tham số chương trình
    - **flink_config**: Cấu hình Flink
    """
    try:
        job_id = await job_service.create_job_config(job_data)
        
        return BaseResponse(
            message="Tạo job config thành công",
            data={"job_id": job_id}
        )
        
    except Exception as e:
        logger.error(f"Lỗi tạo job config: {e}")
        raise handle_exception(e)


@router.get("/", response_model=BaseResponse, summary="Lấy danh sách Job Configs")
async def list_job_configs(
    page: int = Query(1, ge=1, description="Số trang"),
    size: int = Query(20, ge=1, le=100, description="Kích thước trang"),
    status: Optional[JobStatus] = Query(None, description="Lọc theo trạng thái"),
    created_by: Optional[str] = Query(None, description="Lọc theo người tạo"),
    sort_by: str = Query("created_at", description="Trường sắp xếp"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp")
):
    """
    Lấy danh sách job configs với phân trang và lọc
    """
    try:
        jobs, total = await job_service.list_job_configs(
            page=page,
            size=size,
            status=status,
            created_by=created_by,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        job_responses = []
        for job in jobs:
            job_responses.append(JobConfigResponse(**job.dict()))
        
        return BaseResponse(
            data={
                "jobs": job_responses,
                "total": total,
                "page": page,
                "size": size
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi lấy danh sách job configs: {e}")
        raise handle_exception(e)


@router.get("/{job_id}", response_model=BaseResponse, summary="Lấy Job Config theo ID")
async def get_job_config(job_id: str):
    """
    Lấy thông tin chi tiết của job config theo ID
    """
    try:
        job = await job_service.get_job_config(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job config với ID {job_id} không tồn tại"
            )
        
        return BaseResponse(data=JobConfigResponse(**job.dict()))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi lấy job config: {e}")
        raise handle_exception(e)


@router.put("/{job_id}", response_model=BaseResponse, summary="Cập nhật Job Config")
async def update_job_config(job_id: str, update_data: JobConfigUpdate):
    """
    Cập nhật job configuration
    """
    try:
        success = await job_service.update_job_config(job_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job config với ID {job_id} không tồn tại"
            )
        
        return BaseResponse(message="Cập nhật job config thành công")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi cập nhật job config: {e}")
        raise handle_exception(e)


@router.delete("/{job_id}", response_model=BaseResponse, summary="Xóa Job Config")
async def delete_job_config(job_id: str):
    """
    Xóa job configuration
    """
    try:
        success = await job_service.delete_job_config(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job config với ID {job_id} không tồn tại"
            )
        
        return BaseResponse(message="Xóa job config thành công")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi xóa job config: {e}")
        raise handle_exception(e)


@router.post("/{job_id}/deploy", response_model=BaseResponse, summary="Deploy Job")
async def deploy_job(job_id: str, deploy_request: JobDeployRequest):
    """
    Deploy job lên Flink cluster
    
    - **deployed_by**: Người thực hiện deploy
    """
    try:
        result = await job_service.deploy_job(job_id, deploy_request)
        
        return BaseResponse(
            message="Deploy job thành công",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Lỗi deploy job: {e}")
        raise handle_exception(e)


@router.post("/{job_id}/stop", response_model=BaseResponse, summary="Stop Job")
async def stop_job(job_id: str, stop_request: JobStopRequest):
    """
    Stop job trên Flink cluster
    
    - **savepoint**: Tạo savepoint trước khi stop
    - **savepoint_path**: Đường dẫn savepoint
    """
    try:
        result = await job_service.stop_job(
            job_id, 
            savepoint=stop_request.savepoint,
            savepoint_path=stop_request.savepoint_path
        )
        
        return BaseResponse(
            message="Stop job thành công",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Lỗi stop job: {e}")
        raise handle_exception(e)


@router.get("/{job_id}/history", response_model=BaseResponse, summary="Lấy lịch sử Deployment")
async def get_deployment_history(job_id: str):
    """
    Lấy lịch sử deployment của job
    """
    try:
        history = await job_service.get_deployment_history(job_id)
        
        history_responses = []
        for h in history:
            history_responses.append(DeploymentHistoryResponse(**h.dict()))
        
        return BaseResponse(
            data={
                "job_id": job_id,
                "deployments": history_responses,
                "total": len(history_responses)
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi lấy deployment history: {e}")
        raise handle_exception(e)


@router.get("/name/{job_name}", response_model=BaseResponse, summary="Lấy Job Config theo tên")
async def get_job_config_by_name(job_name: str):
    """
    Lấy thông tin job config theo tên
    """
    try:
        job = await job_service.get_job_config_by_name(job_name)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job config với tên {job_name} không tồn tại"
            )
        
        return BaseResponse(data=JobConfigResponse(**job.dict()))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi lấy job config: {e}")
        raise handle_exception(e)

