from app.services.mongo_service import mongo_service
from app.services.minio_service import minio_service
from app.models.artifact import Artifact, ArtifactMetadata
from app.schemas.artifact import ArtifactCreate, ArtifactMetadataCreate
from app.core.exceptions import ArtifactNotFoundError, ArtifactVersionExistsError, MinIOError
from typing import List, Optional, BinaryIO
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ArtifactService:
    """Service để quản lý artifacts"""
    
    def __init__(self):
        self.mongo_service = mongo_service
        self.minio_service = minio_service
    
    async def create_artifact(self, artifact_data: ArtifactCreate, file_data: BinaryIO, file_size: int) -> str:
        """Tạo artifact mới"""
        try:
            # Upload file lên MinIO
            minio_path, file_hash = self.minio_service.upload_artifact(
                artifact_data.metadata.artifact_name,
                artifact_data.metadata.version,
                file_data,
                file_size
            )
            
            # Tạo metadata
            metadata = ArtifactMetadata(
                artifact_name=artifact_data.metadata.artifact_name,
                version=artifact_data.metadata.version,
                hash=file_hash,
                entry_classes=artifact_data.metadata.entry_classes,
                uploaded_by=artifact_data.metadata.uploaded_by,
                uploaded_at=datetime.utcnow(),
                file_size=file_size,
                description=artifact_data.metadata.description
            )
            
            # Tạo artifact model
            artifact = Artifact(
                artifact_name=artifact_data.metadata.artifact_name,
                version=artifact_data.metadata.version,
                metadata=metadata,
                minio_path=minio_path
            )
            
            # Lưu vào MongoDB
            artifact_id = await self.mongo_service.create_artifact(artifact)
            
            logger.info(f"Đã tạo artifact thành công: {artifact_id}")
            return artifact_id
            
        except ArtifactVersionExistsError:
            # Xóa file đã upload nếu có lỗi
            try:
                self.minio_service.delete_artifact(minio_path)
            except:
                pass
            raise
        except Exception as e:
            # Xóa file đã upload nếu có lỗi
            try:
                self.minio_service.delete_artifact(minio_path)
            except:
                pass
            logger.error(f"Lỗi tạo artifact: {e}")
            raise
    
    async def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Lấy artifact theo ID"""
        return await self.mongo_service.get_artifact_by_id(artifact_id)
    
    async def get_artifact_by_name_version(self, artifact_name: str, version: str) -> Optional[Artifact]:
        """Lấy artifact theo tên và phiên bản"""
        return await self.mongo_service.get_artifact_by_name_version(artifact_name, version)
    
    async def list_artifacts(self, page: int = 1, size: int = 20, 
                           artifact_name: Optional[str] = None,
                           sort_by: str = "created_at", sort_order: str = "desc") -> tuple[List[Artifact], int]:
        """Lấy danh sách artifacts với phân trang"""
        skip = (page - 1) * size
        sort_direction = -1 if sort_order == "desc" else 1
        
        artifacts = await self.mongo_service.list_artifacts(
            skip=skip,
            limit=size,
            artifact_name=artifact_name,
            sort_by=sort_by,
            sort_order=sort_direction
        )
        
        total = await self.mongo_service.count_artifacts(artifact_name)
        
        return artifacts, total
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """Xóa artifact"""
        try:
            # Lấy artifact để có minio_path
            artifact = await self.mongo_service.get_artifact_by_id(artifact_id)
            if not artifact:
                raise ArtifactNotFoundError(artifact_id)
            
            # Xóa file từ MinIO
            self.minio_service.delete_artifact(artifact.minio_path)
            
            # Xóa record từ MongoDB
            success = await self.mongo_service.delete_artifact(artifact_id)
            
            if success:
                logger.info(f"Đã xóa artifact thành công: {artifact_id}")
            
            return success
            
        except ArtifactNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Lỗi xóa artifact: {e}")
            raise
    
    async def download_artifact(self, artifact_id: str) -> tuple[bytes, str]:
        """Download artifact JAR file"""
        try:
            artifact = await self.mongo_service.get_artifact_by_id(artifact_id)
            if not artifact:
                raise ArtifactNotFoundError(artifact_id)
            
            file_data = self.minio_service.download_artifact(artifact.minio_path)
            filename = f"{artifact.artifact_name}-{artifact.version}.jar"
            
            return file_data, filename
            
        except ArtifactNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Lỗi download artifact: {e}")
            raise
    
    async def get_artifact_versions(self, artifact_name: str) -> List[str]:
        """Lấy danh sách phiên bản của artifact"""
        return await self.mongo_service.get_artifact_versions(artifact_name)
    
    async def search_artifacts(self, query: str) -> List[Artifact]:
        """Tìm kiếm artifacts"""
        return await self.mongo_service.search_artifacts(query)
    
    async def generate_upload_url(self, artifact_name: str, version: str) -> str:
        """Tạo presigned URL để upload artifact"""
        try:
            minio_path = f"artifacts/{artifact_name}/versions/{version}/fatjar/{artifact_name}-{version}.jar"
            return self.minio_service.generate_presigned_url(minio_path)
        except Exception as e:
            logger.error(f"Lỗi tạo upload URL: {e}")
            raise MinIOError(f"Không thể tạo upload URL: {e}")


# Global instance
artifact_service = ArtifactService()

