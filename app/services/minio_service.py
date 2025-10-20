from minio import Minio
from minio.error import S3Error
from app.config import settings
from app.core.exceptions import MinIOError
from app.services.mock_services import mock_minio_service
import logging
from typing import Optional, BinaryIO
import hashlib
import os
from datetime import timedelta

logger = logging.getLogger(__name__)


class MinIOService:
    """Service để tương tác với MinIO"""
    
    def __init__(self):
        self.use_mock = True  # Sử dụng mock service
        self.bucket_name = settings.minio_bucket
        
        if not self.use_mock:
            try:
                self.client = Minio(
                    settings.minio_endpoint,
                    access_key=settings.minio_access_key,
                    secret_key=settings.minio_secret_key,
                    secure=settings.minio_secure
                )
                self._ensure_bucket_exists()
            except Exception as e:
                logger.warning(f"MinIO connection failed, using mock: {e}")
                self.use_mock = True
    
    def _ensure_bucket_exists(self):
        """Đảm bảo bucket tồn tại"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Đã tạo bucket {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Lỗi tạo bucket: {e}")
            raise MinIOError(f"Không thể tạo bucket: {e}")
    
    def upload_artifact(self, artifact_name: str, version: str, file_data: BinaryIO, file_size: int) -> tuple[str, str]:
        """
        Upload artifact JAR file
        Returns: (minio_path, file_hash)
        """
        if self.use_mock:
            return mock_minio_service.upload_artifact(artifact_name, version, file_data, file_size)
        
        try:
            # Tạo đường dẫn trong MinIO
            minio_path = f"artifacts/{artifact_name}/versions/{version}/fatjar/{artifact_name}-{version}.jar"
            
            # Tính hash của file
            file_data.seek(0)
            file_hash = hashlib.sha256(file_data.read()).hexdigest()
            file_data.seek(0)
            
            # Upload file
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=minio_path,
                data=file_data,
                length=file_size,
                content_type="application/java-archive"
            )
            
            logger.info(f"Đã upload artifact: {minio_path}")
            return minio_path, file_hash
            
        except S3Error as e:
            logger.error(f"Lỗi upload artifact: {e}")
            raise MinIOError(f"Không thể upload artifact: {e}")
    
    def download_artifact(self, minio_path: str) -> bytes:
        """Download artifact JAR file"""
        if self.use_mock:
            return mock_minio_service.download_artifact(minio_path)
        
        try:
            response = self.client.get_object(self.bucket_name, minio_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
            
        except S3Error as e:
            logger.error(f"Lỗi download artifact: {e}")
            raise MinIOError(f"Không thể download artifact: {e}")
    
    def delete_artifact(self, minio_path: str) -> bool:
        """Xóa artifact JAR file"""
        if self.use_mock:
            return mock_minio_service.delete_artifact(minio_path)
        
        try:
            self.client.remove_object(self.bucket_name, minio_path)
            logger.info(f"Đã xóa artifact: {minio_path}")
            return True
            
        except S3Error as e:
            logger.error(f"Lỗi xóa artifact: {e}")
            raise MinIOError(f"Không thể xóa artifact: {e}")
    
    def artifact_exists(self, minio_path: str) -> bool:
        """Kiểm tra artifact có tồn tại không"""
        if self.use_mock:
            return mock_minio_service.artifact_exists(minio_path)
        
        try:
            self.client.stat_object(self.bucket_name, minio_path)
            return True
        except S3Error:
            return False
    
    def get_artifact_info(self, minio_path: str) -> dict:
        """Lấy thông tin artifact"""
        if self.use_mock:
            return mock_minio_service.get_artifact_info(minio_path)
        
        try:
            stat = self.client.stat_object(self.bucket_name, minio_path)
            return {
                "size": stat.size,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
                "content_type": stat.content_type
            }
        except S3Error as e:
            logger.error(f"Lỗi lấy thông tin artifact: {e}")
            raise MinIOError(f"Không thể lấy thông tin artifact: {e}")
    
    def generate_presigned_url(self, minio_path: str, expires_in: int = 3600) -> str:
        """Tạo presigned URL để upload/download"""
        if self.use_mock:
            return mock_minio_service.generate_presigned_url(minio_path, expires_in)
        
        try:
            url = self.client.presigned_put_object(
                bucket_name=self.bucket_name,
                object_name=minio_path,
                expires=timedelta(seconds=expires_in)
            )
            return url
        except S3Error as e:
            logger.error(f"Lỗi tạo presigned URL: {e}")
            raise MinIOError(f"Không thể tạo presigned URL: {e}")


# Global instance
minio_service = MinIOService()