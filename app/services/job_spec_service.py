from app.services.mongo_service import mongo_service
from app.core.database import get_database
from app.models.job_config import JobSpec, Execution, ExecutionHistory, JobStatus
from app.schemas.job_config import JobSpecCreate, JobSpecUpdate, ExecutionCreate
from app.core.exceptions import JobConfigNotFoundError, JobNameExistsError, FlinkClusterError, ArtifactNotFoundError
from app.services.mock_services import mock_mongo_service
from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging
import httpx
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)


class JobSpecService:
    """Service để quản lý Job Specifications"""
    
    def __init__(self):
        self.mongo_service = mongo_service
        self.use_mock = True  # Sử dụng mock mode
        self.db = None
        
        if not self.use_mock:
            try:
                self.db = get_database()
            except Exception as e:
                logger.warning(f"Database connection failed, using mock: {e}")
                self.use_mock = True
    
    async def create_job_spec(self, job_spec_data: JobSpecCreate) -> str:
        """Tạo job spec mới"""
        if self.use_mock:
            # Mock implementation
            job_spec_id = f"job_spec_{len(mock_mongo_service.job_specs) + 1}"
            job_spec_dict = {
                "_id": job_spec_id,
                "job_spec_name": job_spec_data.job_spec_name,
                "artifact_id": job_spec_data.artifact_id,
                "entry_class": job_spec_data.entry_class,
                "parallelism": job_spec_data.parallelism,
                "program_args": job_spec_data.program_args or [],
                "savepoint_path": job_spec_data.savepoint_path,
                "flink_config": job_spec_data.flink_config or {},
                "created_by": job_spec_data.created_by,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            mock_mongo_service.job_specs[job_spec_id] = job_spec_dict
            logger.info(f"Mock tạo job spec: {job_spec_data.job_spec_name}")
            return job_spec_id
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def get_job_spec(self, job_spec_id: str) -> Optional[JobSpec]:
        """Lấy job spec theo ID"""
        if self.use_mock:
            if job_spec_id in mock_mongo_service.job_specs:
                job_spec_doc = mock_mongo_service.job_specs[job_spec_id].copy()
                job_spec_doc["id"] = job_spec_doc["_id"]
                return JobSpec(**job_spec_doc)
            return None
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def list_job_specs(self, page: int = 1, size: int = 20, 
                           job_spec_name: Optional[str] = None,
                           created_by: Optional[str] = None,
                           sort_by: str = "created_at", sort_order: str = "desc") -> tuple[List[JobSpec], int]:
        """Lấy danh sách job specs với phân trang"""
        if self.use_mock:
            job_specs = []
            for job_spec_id, job_spec_doc in mock_mongo_service.job_specs.items():
                if job_spec_name:
                    if job_spec_name.lower() not in job_spec_doc.get("job_spec_name", "").lower():
                        continue
                if created_by:
                    if job_spec_doc.get("created_by") != created_by:
                        continue
                
                job_spec_doc = job_spec_doc.copy()
                job_spec_doc["id"] = job_spec_doc["_id"]
                job_specs.append(JobSpec(**job_spec_doc))
            
            # Simple pagination
            skip = (page - 1) * size
            total = len(job_specs)
            job_specs = job_specs[skip:skip + size]
            
            return job_specs, total
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def update_job_spec(self, job_spec_id: str, update_data: JobSpecUpdate) -> bool:
        """Cập nhật job spec"""
        if self.use_mock:
            if job_spec_id not in mock_mongo_service.job_specs:
                return False
            
            job_spec_doc = mock_mongo_service.job_specs[job_spec_id]
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            job_spec_doc.update(update_dict)
            logger.info(f"Mock cập nhật job spec: {job_spec_id}")
            return True
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def delete_job_spec(self, job_spec_id: str) -> bool:
        """Xóa job spec"""
        if self.use_mock:
            if job_spec_id in mock_mongo_service.job_specs:
                del mock_mongo_service.job_specs[job_spec_id]
                logger.info(f"Mock xóa job spec: {job_spec_id}")
                return True
            return False
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")


class ExecutionService:
    """Service để quản lý Executions"""
    
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
    
    async def start_execution(self, job_spec_id: str, execution_data: ExecutionCreate) -> Dict[str, Any]:
        """Bắt đầu execution từ job spec"""
        if self.use_mock:
            # Mock implementation
            execution_id = f"exec_{len(mock_mongo_service.executions) + 1}"
            flink_job_id = f"flink_job_{execution_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Tạo execution record
            execution_dict = {
                "_id": execution_id,
                "job_spec_id": job_spec_id,
                "flink_job_id": flink_job_id,
                "status": "running",
                "started_by": execution_data.started_by,
                "started_at": datetime.utcnow(),
                "finished_at": None,
                "error_message": None
            }
            mock_mongo_service.executions[execution_id] = execution_dict
            
            # Tạo execution history
            history_id = f"history_{len(mock_mongo_service.execution_history) + 1}"
            history_dict = {
                "_id": history_id,
                "execution_id": execution_id,
                "performed_by": execution_data.started_by,
                "performed_at": datetime.utcnow(),
                "action": "START",
                "old_status": None,
                "new_status": "running",
                "details": {"job_spec_id": job_spec_id}
            }
            mock_mongo_service.execution_history[history_id] = history_dict
            
            logger.info(f"Mock start execution: {execution_id} -> {flink_job_id}")
            
            return {
                "execution_id": execution_id,
                "flink_job_id": flink_job_id,
                "status": "running",
                "started_at": datetime.utcnow(),
                "started_by": execution_data.started_by
            }
        
        # Real implementation would go here
        raise NotImplementedError("Real Flink execution not available")
    
    async def stop_execution(self, execution_id: str, savepoint: bool = False, savepoint_path: Optional[str] = None) -> Dict[str, Any]:
        """Dừng execution"""
        if self.use_mock:
            # Mock stop execution
            execution_doc = mock_mongo_service.executions.get(execution_id, {})
            flink_job_id = execution_doc.get("flink_job_id", f"flink_job_{execution_id}")
            
            # Cập nhật execution
            if execution_id in mock_mongo_service.executions:
                mock_mongo_service.executions[execution_id]["status"] = "canceled"
                mock_mongo_service.executions[execution_id]["finished_at"] = datetime.utcnow()
            
            # Tạo execution history
            history_id = f"history_{len(mock_mongo_service.execution_history) + 1}"
            history_dict = {
                "_id": history_id,
                "execution_id": execution_id,
                "performed_by": "system",  # Mock user
                "performed_at": datetime.utcnow(),
                "action": "STOP",
                "old_status": "running",
                "new_status": "canceled",
                "details": {"savepoint": savepoint, "savepoint_path": savepoint_path}
            }
            mock_mongo_service.execution_history[history_id] = history_dict
            
            logger.info(f"Mock stop execution: {execution_id}")
            
            return {
                "execution_id": execution_id,
                "flink_job_id": flink_job_id,
                "status": "canceled",
                "stopped_at": datetime.utcnow(),
                "savepoint_path": savepoint_path if savepoint else None
            }
        
        # Real implementation would go here
        raise NotImplementedError("Real Flink stop not available")
    
    async def get_execution(self, execution_id: str) -> Optional[Execution]:
        """Lấy execution theo ID"""
        if self.use_mock:
            if execution_id in mock_mongo_service.executions:
                execution_doc = mock_mongo_service.executions[execution_id].copy()
                execution_doc["id"] = execution_doc["_id"]
                return Execution(**execution_doc)
            return None
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def list_executions(self, page: int = 1, size: int = 20, 
                            job_spec_id: Optional[str] = None,
                            status: Optional[JobStatus] = None,
                            started_by: Optional[str] = None,
                            sort_by: str = "started_at", sort_order: str = "desc") -> tuple[List[Execution], int]:
        """Lấy danh sách executions với phân trang"""
        if self.use_mock:
            executions = []
            for execution_id, execution_doc in mock_mongo_service.executions.items():
                if job_spec_id:
                    if execution_doc.get("job_spec_id") != job_spec_id:
                        continue
                if status:
                    if execution_doc.get("status") != status:
                        continue
                if started_by:
                    if execution_doc.get("started_by") != started_by:
                        continue
                
                execution_doc = execution_doc.copy()
                execution_doc["id"] = execution_doc["_id"]
                executions.append(Execution(**execution_doc))
            
            # Simple pagination
            skip = (page - 1) * size
            total = len(executions)
            executions = executions[skip:skip + size]
            
            return executions, total
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")
    
    async def get_execution_history(self, execution_id: str) -> List[ExecutionHistory]:
        """Lấy lịch sử execution"""
        if self.use_mock:
            history = []
            for history_id, history_doc in mock_mongo_service.execution_history.items():
                if history_doc.get("execution_id") == execution_id:
                    history_doc = history_doc.copy()
                    history_doc["id"] = history_doc["_id"]
                    history.append(ExecutionHistory(**history_doc))
            
            # Sort by performed_at desc
            history.sort(key=lambda x: x.performed_at, reverse=True)
            return history
        
        # Real implementation would go here
        raise NotImplementedError("Real MongoDB implementation not available")


# Global instances
job_spec_service = JobSpecService()
execution_service = ExecutionService()
