from app.services.mongo_service import mongo_service
from app.core.database import get_database
from app.models.job_config import JobConfig, DeploymentHistory, JobStatus
from app.schemas.job_config import JobConfigCreate, JobConfigUpdate, JobDeployRequest
from app.core.exceptions import JobConfigNotFoundError, JobNameExistsError, FlinkClusterError, ArtifactNotFoundError
from app.services.mock_services import mock_mongo_service
from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging
import httpx
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)


class JobService:
    """Service để quản lý job configs"""
    
    def __init__(self):
        self.mongo_service = mongo_service
        self.use_mock = True  # Sử dụng mock mode
        self.db = None
        self.flink_api_url = settings.flink_rest_api_url
        
        if not self.use_mock:
            try:
                self.db = get_database()
            except Exception as e:
                logger.warning(f"Database connection failed, using mock: {e}")
                self.use_mock = True
    
    async def create_job_config(self, job_data: JobConfigCreate) -> str:
        """Tạo job config mới"""
        if self.use_mock:
            # Mock implementation
            job_id = f"job_{len(mock_mongo_service.job_configs) + 1}"
            job_dict = {
                "_id": job_id,
                "job_name": job_data.job_name,
                "artifact_id": job_data.artifact_id,
                "entry_class": job_data.entry_class,
                "parallelism": job_data.parallelism,
                "program_args": job_data.program_args or [],
                "savepoint_path": job_data.savepoint_path,
                "flink_config": job_data.flink_config or {},
                "status": "created",
                "created_by": job_data.created_by,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            mock_mongo_service.job_configs[job_id] = job_dict
            logger.info(f"Mock tạo job config: {job_data.job_name}")
            return job_id
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def get_job_config(self, job_id: str) -> Optional[JobConfig]:
        """Lấy job config theo ID"""
        if self.use_mock:
            if job_id in mock_mongo_service.job_configs:
                job_doc = mock_mongo_service.job_configs[job_id].copy()
                job_doc["id"] = job_doc["_id"]
                return JobConfig(**job_doc)
            return None
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def get_job_config_by_name(self, job_name: str) -> Optional[JobConfig]:
        """Lấy job config theo tên"""
        if self.use_mock:
            for job_id, job_doc in mock_mongo_service.job_configs.items():
                if job_doc.get("job_name") == job_name:
                    job_doc = job_doc.copy()
                    job_doc["id"] = job_doc["_id"]
                    return JobConfig(**job_doc)
            return None
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def list_job_configs(self, page: int = 1, size: int = 20, 
                             status: Optional[JobStatus] = None,
                             created_by: Optional[str] = None,
                             sort_by: str = "created_at", sort_order: str = "desc") -> tuple[List[JobConfig], int]:
        """Lấy danh sách job configs với phân trang"""
        if self.use_mock:
            jobs = []
            for job_id, job_doc in mock_mongo_service.job_configs.items():
                if status and job_doc.get("status") != status:
                    continue
                if created_by and job_doc.get("created_by") != created_by:
                    continue
                
                job_doc = job_doc.copy()
                job_doc["id"] = job_doc["_id"]
                jobs.append(JobConfig(**job_doc))
            
            # Simple pagination
            skip = (page - 1) * size
            total = len(jobs)
            jobs = jobs[skip:skip + size]
            
            return jobs, total
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def update_job_config(self, job_id: str, update_data: JobConfigUpdate) -> bool:
        """Cập nhật job config"""
        if self.use_mock:
            if job_id not in mock_mongo_service.job_configs:
                return False
            
            job_doc = mock_mongo_service.job_configs[job_id]
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            job_doc.update(update_dict)
            logger.info(f"Mock cập nhật job config: {job_id}")
            return True
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def delete_job_config(self, job_id: str) -> bool:
        """Xóa job config"""
        if self.use_mock:
            if job_id in mock_mongo_service.job_configs:
                del mock_mongo_service.job_configs[job_id]
                logger.info(f"Mock xóa job config: {job_id}")
                return True
            return False
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def deploy_job(self, job_id: str, deploy_request: JobDeployRequest) -> Dict[str, Any]:
        """Deploy job lên Flink cluster (mock)"""
        if self.use_mock:
            # Mock deployment
            flink_job_id = f"flink_job_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Cập nhật job config
            if job_id in mock_mongo_service.job_configs:
                mock_mongo_service.job_configs[job_id]["flink_job_id"] = flink_job_id
                mock_mongo_service.job_configs[job_id]["status"] = "running"
                mock_mongo_service.job_configs[job_id]["last_deployed_at"] = datetime.utcnow()
                mock_mongo_service.job_configs[job_id]["updated_at"] = datetime.utcnow()
            
            # Lưu deployment history
            deployment_id = f"deploy_{len(mock_mongo_service.deployment_history) + 1}"
            deployment = {
                "_id": deployment_id,
                "job_id": job_id,
                "artifact_id": mock_mongo_service.job_configs.get(job_id, {}).get("artifact_id", ""),
                "deployed_by": deploy_request.deployed_by,
                "deployed_at": datetime.utcnow(),
                "status": "running",
                "flink_job_id": flink_job_id
            }
            mock_mongo_service.deployment_history[deployment_id] = deployment
            
            logger.info(f"Mock deploy job: {job_id} -> {flink_job_id}")
            
            return {
                "job_id": job_id,
                "flink_job_id": flink_job_id,
                "status": "running",
                "deployed_at": datetime.utcnow(),
                "deployed_by": deploy_request.deployed_by
            }
        
        # Real implementation would go here
        raise NotImplementedError("Real Flink deployment not available")
    
    async def stop_job(self, job_id: str, savepoint: bool = False, savepoint_path: Optional[str] = None) -> Dict[str, Any]:
        """Stop job trên Flink cluster (mock)"""
        if self.use_mock:
            # Mock stop job
            job_doc = mock_mongo_service.job_configs.get(job_id, {})
            flink_job_id = job_doc.get("flink_job_id", f"flink_job_{job_id}")
            
            # Cập nhật job config
            if job_id in mock_mongo_service.job_configs:
                mock_mongo_service.job_configs[job_id]["status"] = "canceled"
                mock_mongo_service.job_configs[job_id]["updated_at"] = datetime.utcnow()
            
            logger.info(f"Mock stop job: {job_id}")
            
            return {
                "job_id": job_id,
                "flink_job_id": flink_job_id,
                "status": "canceled",
                "stopped_at": datetime.utcnow(),
                "savepoint_path": savepoint_path if savepoint else None
            }
        
        # Real implementation would go here
        raise NotImplementedError("Real Flink stop not available")
    
    async def get_deployment_history(self, job_id: str) -> List[DeploymentHistory]:
        """Lấy lịch sử deployment của job"""
        if self.use_mock:
            history = []
            for deployment_id, deployment_doc in mock_mongo_service.deployment_history.items():
                if deployment_doc.get("job_id") == job_id:
                    deployment_doc = deployment_doc.copy()
                    deployment_doc["id"] = deployment_doc["_id"]
                    history.append(DeploymentHistory(**deployment_doc))
            
            # Sort by deployed_at desc
            history.sort(key=lambda x: x.deployed_at, reverse=True)
            return history
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")


# Global instance
job_service = JobService()