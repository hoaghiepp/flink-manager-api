from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re


class ArtifactMetadataCreate(BaseModel):
    """Schema để tạo metadata artifact"""
    artifact_name: str = Field(..., description="Tên artifact", min_length=1, max_length=100)
    version: str = Field(..., description="Phiên bản", pattern=r'^\d+\.\d+\.\d+$')
    entry_classes: List[str] = Field(..., description="Danh sách entry classes", min_items=1)
    uploaded_by: str = Field(..., description="Người upload", min_length=1)
    description: Optional[str] = Field(None, description="Mô tả artifact", max_length=500)
    
    @validator('artifact_name')
    def validate_artifact_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Tên artifact chỉ được chứa chữ cái, số, gạch ngang và gạch dưới')
        return v


class ArtifactMetadataResponse(BaseModel):
    """Response metadata artifact"""
    artifact_name: str
    version: str
    hash: str
    entry_classes: List[str]
    uploaded_by: str
    uploaded_at: datetime
    file_size: int
    description: Optional[str]


class ArtifactCreate(BaseModel):
    """Schema để tạo artifact"""
    metadata: ArtifactMetadataCreate


class ArtifactResponse(BaseModel):
    """Response artifact"""
    id: str
    artifact_name: str
    version: str
    metadata: ArtifactMetadataResponse
    minio_path: str
    created_at: datetime
    updated_at: datetime


class ArtifactListResponse(BaseModel):
    """Response danh sách artifacts"""
    artifacts: List[ArtifactResponse]
    total: int
    page: int
    size: int


class ArtifactUploadResponse(BaseModel):
    """Response upload artifact"""
    artifact_id: str
    upload_url: str
    expires_in: int  # seconds

