from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.database import get_database
from app.models.artifact import Artifact, ArtifactMetadata
from app.core.exceptions import ArtifactNotFoundError, ArtifactVersionExistsError
from app.services.mock_services import mock_mongo_service
from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MongoService:
    """Service để tương tác với MongoDB"""
    
    def __init__(self):
        self.use_mock = True  # Sử dụng mock service
        self.db: Optional[AsyncIOMotorDatabase] = None
        
        if not self.use_mock:
            try:
                self.db = get_database()
            except Exception as e:
                logger.warning(f"MongoDB connection failed, using mock: {e}")
                self.use_mock = True
    
    # Artifact operations
    async def create_artifact(self, artifact: Artifact) -> str:
        """Tạo artifact mới"""
        if self.use_mock:
            return await mock_mongo_service.create_artifact(artifact)
        
        try:
            # Kiểm tra artifact đã tồn tại chưa
            existing = await self.db.artifacts.find_one({
                "artifact_name": artifact.artifact_name,
                "version": artifact.version
            })
            
            if existing:
                raise ArtifactVersionExistsError(artifact.artifact_name, artifact.version)
            
            # Chuyển đổi model thành dict
            artifact_dict = artifact.dict(by_alias=True, exclude={"id"})
            
            # Insert vào database
            result = await self.db.artifacts.insert_one(artifact_dict)
            
            logger.info(f"Đã tạo artifact: {artifact.artifact_name} v{artifact.version}")
            return str(result.inserted_id)
            
        except ArtifactVersionExistsError:
            raise
        except Exception as e:
            logger.error(f"Lỗi tạo artifact: {e}")
            raise
    
    async def get_artifact_by_id(self, artifact_id: str) -> Optional[Artifact]:
        """Lấy artifact theo ID"""
        if self.use_mock:
            return await mock_mongo_service.get_artifact_by_id(artifact_id)
        
        try:
            artifact_doc = await self.db.artifacts.find_one({"_id": ObjectId(artifact_id)})
            if artifact_doc:
                artifact_doc["id"] = str(artifact_doc["_id"])
                return Artifact(**artifact_doc)
            return None
            
        except Exception as e:
            logger.error(f"Lỗi lấy artifact: {e}")
            raise
    
    async def get_artifact_by_name_version(self, artifact_name: str, version: str) -> Optional[Artifact]:
        """Lấy artifact theo tên và phiên bản"""
        if self.use_mock:
            return await mock_mongo_service.get_artifact_by_name_version(artifact_name, version)
        
        try:
            artifact_doc = await self.db.artifacts.find_one({
                "artifact_name": artifact_name,
                "version": version
            })
            if artifact_doc:
                artifact_doc["id"] = str(artifact_doc["_id"])
                return Artifact(**artifact_doc)
            return None
            
        except Exception as e:
            logger.error(f"Lỗi lấy artifact: {e}")
            raise
    
    async def list_artifacts(self, skip: int = 0, limit: int = 20, 
                           artifact_name: Optional[str] = None,
                           sort_by: str = "created_at", sort_order: int = -1) -> List[Artifact]:
        """Lấy danh sách artifacts"""
        if self.use_mock:
            return await mock_mongo_service.list_artifacts(skip, limit, artifact_name, sort_by, sort_order)
        
        try:
            filter_dict = {}
            if artifact_name:
                filter_dict["artifact_name"] = {"$regex": artifact_name, "$options": "i"}
            
            cursor = self.db.artifacts.find(filter_dict).sort(sort_by, sort_order).skip(skip).limit(limit)
            artifacts = []
            
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                artifacts.append(Artifact(**doc))
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách artifacts: {e}")
            raise
    
    async def count_artifacts(self, artifact_name: Optional[str] = None) -> int:
        """Đếm số lượng artifacts"""
        if self.use_mock:
            return await mock_mongo_service.count_artifacts(artifact_name)
        
        try:
            filter_dict = {}
            if artifact_name:
                filter_dict["artifact_name"] = {"$regex": artifact_name, "$options": "i"}
            
            count = await self.db.artifacts.count_documents(filter_dict)
            return count
            
        except Exception as e:
            logger.error(f"Lỗi đếm artifacts: {e}")
            raise
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """Xóa artifact"""
        if self.use_mock:
            return await mock_mongo_service.delete_artifact(artifact_id)
        
        try:
            result = await self.db.artifacts.delete_one({"_id": ObjectId(artifact_id)})
            if result.deleted_count > 0:
                logger.info(f"Đã xóa artifact: {artifact_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Lỗi xóa artifact: {e}")
            raise
    
    async def get_artifact_versions(self, artifact_name: str) -> List[str]:
        """Lấy danh sách phiên bản của artifact"""
        if self.use_mock:
            return await mock_mongo_service.get_artifact_versions(artifact_name)
        
        try:
            cursor = self.db.artifacts.find(
                {"artifact_name": artifact_name},
                {"version": 1, "_id": 0}
            ).sort("version", -1)
            
            versions = []
            async for doc in cursor:
                versions.append(doc["version"])
            
            return versions
            
        except Exception as e:
            logger.error(f"Lỗi lấy phiên bản artifact: {e}")
            raise
    
    async def search_artifacts(self, query: str) -> List[Artifact]:
        """Tìm kiếm artifacts"""
        if self.use_mock:
            return await mock_mongo_service.search_artifacts(query)
        
        try:
            filter_dict = {
                "$or": [
                    {"artifact_name": {"$regex": query, "$options": "i"}},
                    {"metadata.description": {"$regex": query, "$options": "i"}},
                    {"metadata.entry_classes": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = self.db.artifacts.find(filter_dict).sort("created_at", -1)
            artifacts = []
            
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                artifacts.append(Artifact(**doc))
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm artifacts: {e}")
            raise


# Global instance
mongo_service = MongoService()