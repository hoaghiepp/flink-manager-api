from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
import io
import logging

from app.services.artifact_service import artifact_service
from app.schemas.artifact import (
    ArtifactCreate, ArtifactResponse, ArtifactListResponse, 
    ArtifactUploadResponse, ArtifactMetadataResponse
)
from app.schemas.common import BaseResponse, ErrorResponse, PaginationParams
from app.core.exceptions import handle_exception

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.post("/upload", response_model=BaseResponse, summary="Upload Artifact")
async def upload_artifact(
    metadata: ArtifactCreate = Depends(),
    file: UploadFile = File(..., description="JAR file của artifact")
):
    """
    Upload artifact JAR file với metadata
    
    - **file**: File JAR của artifact
    - **metadata**: Thông tin metadata của artifact
    """
    try:
        # Kiểm tra file type
        if not file.filename.endswith('.jar'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ chấp nhận file JAR"
            )
        
        # Đọc file data
        file_data = await file.read()
        file_size = len(file_data)
        
        # Tạo artifact
        artifact_id = await artifact_service.create_artifact(
            metadata, 
            io.BytesIO(file_data), 
            file_size
        )
        
        return BaseResponse(
            message="Upload artifact thành công",
            data={"artifact_id": artifact_id}
        )
        
    except Exception as e:
        logger.error(f"Lỗi upload artifact: {e}")
        raise handle_exception(e)


@router.get("/", response_model=BaseResponse, summary="Lấy danh sách Artifacts")
async def list_artifacts(
    page: int = Query(1, ge=1, description="Số trang"),
    size: int = Query(20, ge=1, le=100, description="Kích thước trang"),
    artifact_name: Optional[str] = Query(None, description="Tìm kiếm theo tên artifact"),
    sort_by: str = Query("created_at", description="Trường sắp xếp"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp")
):
    """
    Lấy danh sách artifacts với phân trang và tìm kiếm
    """
    try:
        artifacts, total = await artifact_service.list_artifacts(
            page=page,
            size=size,
            artifact_name=artifact_name,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Convert to response format
        artifact_responses = []
        for artifact in artifacts:
            artifact_responses.append(ArtifactResponse(
                id=artifact.id,
                artifact_name=artifact.artifact_name,
                version=artifact.version,
                metadata=ArtifactMetadataResponse(**artifact.metadata.dict()),
                minio_path=artifact.minio_path,
                created_at=artifact.created_at,
                updated_at=artifact.updated_at
            ))
        
        return BaseResponse(
            data={
                "artifacts": artifact_responses,
                "total": total,
                "page": page,
                "size": size
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi lấy danh sách artifacts: {e}")
        raise handle_exception(e)


@router.get("/{artifact_id}", response_model=BaseResponse, summary="Lấy Artifact theo ID")
async def get_artifact(artifact_id: str):
    """
    Lấy thông tin chi tiết của artifact theo ID
    """
    try:
        artifact = await artifact_service.get_artifact(artifact_id)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact với ID {artifact_id} không tồn tại"
            )
        
        artifact_response = ArtifactResponse(
            id=artifact.id,
            artifact_name=artifact.artifact_name,
            version=artifact.version,
            metadata=ArtifactMetadataResponse(**artifact.metadata.dict()),
            minio_path=artifact.minio_path,
            created_at=artifact.created_at,
            updated_at=artifact.updated_at
        )
        
        return BaseResponse(data=artifact_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi lấy artifact: {e}")
        raise handle_exception(e)


@router.get("/{artifact_name}/versions", response_model=BaseResponse, summary="Lấy danh sách phiên bản")
async def get_artifact_versions(artifact_name: str):
    """
    Lấy danh sách các phiên bản của artifact
    """
    try:
        versions = await artifact_service.get_artifact_versions(artifact_name)
        
        return BaseResponse(
            data={
                "artifact_name": artifact_name,
                "versions": versions
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi lấy phiên bản artifact: {e}")
        raise handle_exception(e)


@router.get("/{artifact_name}/{version}", response_model=BaseResponse, summary="Lấy Artifact theo tên và phiên bản")
async def get_artifact_by_name_version(artifact_name: str, version: str):
    """
    Lấy thông tin artifact theo tên và phiên bản
    """
    try:
        artifact = await artifact_service.get_artifact_by_name_version(artifact_name, version)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact {artifact_name} phiên bản {version} không tồn tại"
            )
        
        artifact_response = ArtifactResponse(
            id=artifact.id,
            artifact_name=artifact.artifact_name,
            version=artifact.version,
            metadata=ArtifactMetadataResponse(**artifact.metadata.dict()),
            minio_path=artifact.minio_path,
            created_at=artifact.created_at,
            updated_at=artifact.updated_at
        )
        
        return BaseResponse(data=artifact_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi lấy artifact: {e}")
        raise handle_exception(e)


@router.get("/{artifact_id}/download", summary="Download Artifact")
async def download_artifact(artifact_id: str):
    """
    Download artifact JAR file
    """
    try:
        file_data, filename = await artifact_service.download_artifact(artifact_id)
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type="application/java-archive",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Lỗi download artifact: {e}")
        raise handle_exception(e)


@router.delete("/{artifact_id}", response_model=BaseResponse, summary="Xóa Artifact")
async def delete_artifact(artifact_id: str):
    """
    Xóa artifact và file JAR tương ứng
    """
    try:
        success = await artifact_service.delete_artifact(artifact_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact với ID {artifact_id} không tồn tại"
            )
        
        return BaseResponse(message="Xóa artifact thành công")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi xóa artifact: {e}")
        raise handle_exception(e)


@router.get("/search/{query}", response_model=BaseResponse, summary="Tìm kiếm Artifacts")
async def search_artifacts(query: str):
    """
    Tìm kiếm artifacts theo từ khóa
    """
    try:
        artifacts = await artifact_service.search_artifacts(query)
        
        artifact_responses = []
        for artifact in artifacts:
            artifact_responses.append(ArtifactResponse(
                id=artifact.id,
                artifact_name=artifact.artifact_name,
                version=artifact.version,
                metadata=ArtifactMetadataResponse(**artifact.metadata.dict()),
                minio_path=artifact.minio_path,
                created_at=artifact.created_at,
                updated_at=artifact.updated_at
            ))
        
        return BaseResponse(
            data={
                "artifacts": artifact_responses,
                "total": len(artifact_responses),
                "query": query
            }
        )
        
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm artifacts: {e}")
        raise handle_exception(e)

