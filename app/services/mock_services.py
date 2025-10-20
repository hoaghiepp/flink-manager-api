from typing import Dict, Any, Optional, List, BinaryIO
import logging
from datetime import datetime
import hashlib
import io

logger = logging.getLogger(__name__)


class MockMinIOService:
    """Mock MinIO service để test mà không cần MinIO thực tế"""
    
    def __init__(self):
        self.files: Dict[str, bytes] = {}
        logger.info("Mock MinIO service initialized")
    
    def _ensure_bucket_exists(self):
        """Mock bucket creation"""
        pass
    
    def upload_artifact(self, artifact_name: str, version: str, file_data: BinaryIO, file_size: int) -> tuple[str, str]:
        """Mock upload artifact"""
        try:
            minio_path = f"artifacts/{artifact_name}/versions/{version}/fatjar/{artifact_name}-{version}.jar"
            
            # Đọc và tính hash
            file_data.seek(0)
            file_content = file_data.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Lưu vào mock storage
            self.files[minio_path] = file_content
            
            logger.info(f"Mock upload artifact: {minio_path}")
            return minio_path, file_hash
            
        except Exception as e:
            logger.error(f"Mock upload error: {e}")
            raise Exception(f"Mock upload failed: {e}")
    
    def download_artifact(self, minio_path: str) -> bytes:
        """Mock download artifact"""
        try:
            if minio_path not in self.files:
                raise Exception(f"File not found: {minio_path}")
            
            logger.info(f"Mock download artifact: {minio_path}")
            return self.files[minio_path]
            
        except Exception as e:
            logger.error(f"Mock download error: {e}")
            raise Exception(f"Mock download failed: {e}")
    
    def delete_artifact(self, minio_path: str) -> bool:
        """Mock delete artifact"""
        try:
            if minio_path in self.files:
                del self.files[minio_path]
                logger.info(f"Mock delete artifact: {minio_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Mock delete error: {e}")
            raise Exception(f"Mock delete failed: {e}")
    
    def artifact_exists(self, minio_path: str) -> bool:
        """Mock check artifact exists"""
        return minio_path in self.files
    
    def get_artifact_info(self, minio_path: str) -> dict:
        """Mock get artifact info"""
        if minio_path not in self.files:
            raise Exception(f"File not found: {minio_path}")
        
        file_content = self.files[minio_path]
        return {
            "size": len(file_content),
            "last_modified": datetime.utcnow(),
            "etag": hashlib.md5(file_content).hexdigest(),
            "content_type": "application/java-archive"
        }
    
    def generate_presigned_url(self, minio_path: str, expires_in: int = 3600) -> str:
        """Mock generate presigned URL"""
        return f"http://mock-minio:9000/{minio_path}?expires={expires_in}"


class MockMongoService:
    """Mock MongoDB service để test mà không cần MongoDB thực tế"""
    
    def __init__(self):
        self.artifacts: Dict[str, Dict[str, Any]] = {}
        self.job_specs: Dict[str, Dict[str, Any]] = {}
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
        logger.info("Mock MongoDB service initialized")
    
    def _generate_id(self) -> str:
        """Generate mock ID"""
        id_val = self._next_id
        self._next_id += 1
        return str(id_val)
    
    # Artifact operations
    async def create_artifact(self, artifact: Any) -> str:
        """Mock create artifact"""
        try:
            artifact_id = self._generate_id()
            artifact_dict = artifact.dict(by_alias=True, exclude={"id"})
            artifact_dict["_id"] = artifact_id
            self.artifacts[artifact_id] = artifact_dict
            
            logger.info(f"Mock create artifact: {artifact_id}")
            return artifact_id
            
        except Exception as e:
            logger.error(f"Mock create artifact error: {e}")
            raise
    
    async def get_artifact_by_id(self, artifact_id: str) -> Optional[Any]:
        """Mock get artifact by ID"""
        try:
            if artifact_id in self.artifacts:
                artifact_doc = self.artifacts[artifact_id].copy()
                artifact_doc["id"] = artifact_doc["_id"]
                return artifact_doc
            return None
            
        except Exception as e:
            logger.error(f"Mock get artifact error: {e}")
            raise
    
    async def get_artifact_by_name_version(self, artifact_name: str, version: str) -> Optional[Any]:
        """Mock get artifact by name and version"""
        try:
            for artifact_id, artifact_doc in self.artifacts.items():
                if (artifact_doc.get("artifact_name") == artifact_name and 
                    artifact_doc.get("version") == version):
                    artifact_doc = artifact_doc.copy()
                    artifact_doc["id"] = artifact_doc["_id"]
                    return artifact_doc
            return None
            
        except Exception as e:
            logger.error(f"Mock get artifact by name/version error: {e}")
            raise
    
    async def list_artifacts(self, skip: int = 0, limit: int = 20, 
                           artifact_name: Optional[str] = None,
                           sort_by: str = "created_at", sort_order: int = -1) -> List[Any]:
        """Mock list artifacts"""
        try:
            artifacts = []
            for artifact_id, artifact_doc in self.artifacts.items():
                if artifact_name:
                    if artifact_name.lower() not in artifact_doc.get("artifact_name", "").lower():
                        continue
                
                artifact_doc = artifact_doc.copy()
                artifact_doc["id"] = artifact_doc["_id"]
                artifacts.append(artifact_doc)
            
            # Simple sorting
            if sort_by in ["created_at", "updated_at"]:
                artifacts.sort(key=lambda x: x.get(sort_by, ""), reverse=(sort_order == -1))
            
            return artifacts[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"Mock list artifacts error: {e}")
            raise
    
    async def count_artifacts(self, artifact_name: Optional[str] = None) -> int:
        """Mock count artifacts"""
        try:
            count = 0
            for artifact_doc in self.artifacts.values():
                if artifact_name:
                    if artifact_name.lower() in artifact_doc.get("artifact_name", "").lower():
                        count += 1
                else:
                    count += 1
            return count
            
        except Exception as e:
            logger.error(f"Mock count artifacts error: {e}")
            raise
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """Mock delete artifact"""
        try:
            if artifact_id in self.artifacts:
                del self.artifacts[artifact_id]
                logger.info(f"Mock delete artifact: {artifact_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Mock delete artifact error: {e}")
            raise
    
    async def get_artifact_versions(self, artifact_name: str) -> List[str]:
        """Mock get artifact versions"""
        try:
            versions = []
            for artifact_doc in self.artifacts.values():
                if artifact_doc.get("artifact_name") == artifact_name:
                    versions.append(artifact_doc.get("version", ""))
            
            # Sort versions (simple string sort)
            versions.sort(reverse=True)
            return versions
            
        except Exception as e:
            logger.error(f"Mock get artifact versions error: {e}")
            raise
    
    async def search_artifacts(self, query: str) -> List[Any]:
        """Mock search artifacts"""
        try:
            results = []
            for artifact_id, artifact_doc in self.artifacts.items():
                # Simple text search
                searchable_text = (
                    artifact_doc.get("artifact_name", "") + " " +
                    artifact_doc.get("version", "") + " " +
                    artifact_doc.get("metadata", {}).get("description", "")
                ).lower()
                
                if query.lower() in searchable_text:
                    artifact_doc = artifact_doc.copy()
                    artifact_doc["id"] = artifact_doc["_id"]
                    results.append(artifact_doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Mock search artifacts error: {e}")
            raise
    
    # JobSpec operations
    async def create_job_spec(self, job_spec: Any) -> str:
        """Mock create job spec"""
        try:
            job_spec_id = self._generate_id()
            job_spec_dict = job_spec.dict(by_alias=True, exclude={"id"})
            job_spec_dict["_id"] = job_spec_id
            self.job_specs[job_spec_id] = job_spec_dict
            
            logger.info(f"Mock create job spec: {job_spec_id}")
            return job_spec_id
            
        except Exception as e:
            logger.error(f"Mock create job spec error: {e}")
            raise
    
    async def get_job_spec_by_id(self, job_spec_id: str) -> Optional[Any]:
        """Mock get job spec by ID"""
        try:
            if job_spec_id in self.job_specs:
                job_spec_doc = self.job_specs[job_spec_id].copy()
                job_spec_doc["id"] = job_spec_doc["_id"]
                return job_spec_doc
            return None
            
        except Exception as e:
            logger.error(f"Mock get job spec error: {e}")
            raise
    
    async def list_job_specs(self, skip: int = 0, limit: int = 20, 
                           job_spec_name: Optional[str] = None,
                           created_by: Optional[str] = None,
                           sort_by: str = "created_at", sort_order: int = -1) -> List[Any]:
        """Mock list job specs"""
        try:
            job_specs = []
            for job_spec_id, job_spec_doc in self.job_specs.items():
                if job_spec_name:
                    if job_spec_name.lower() not in job_spec_doc.get("job_spec_name", "").lower():
                        continue
                if created_by:
                    if job_spec_doc.get("created_by") != created_by:
                        continue
                
                job_spec_doc = job_spec_doc.copy()
                job_spec_doc["id"] = job_spec_doc["_id"]
                job_specs.append(job_spec_doc)
            
            # Simple sorting
            if sort_by in ["created_at", "updated_at"]:
                job_specs.sort(key=lambda x: x.get(sort_by, ""), reverse=(sort_order == -1))
            
            return job_specs[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"Mock list job specs error: {e}")
            raise
    
    async def count_job_specs(self, job_spec_name: Optional[str] = None, created_by: Optional[str] = None) -> int:
        """Mock count job specs"""
        try:
            count = 0
            for job_spec_doc in self.job_specs.values():
                if job_spec_name:
                    if job_spec_name.lower() not in job_spec_doc.get("job_spec_name", "").lower():
                        continue
                if created_by:
                    if job_spec_doc.get("created_by") != created_by:
                        continue
                count += 1
            return count
            
        except Exception as e:
            logger.error(f"Mock count job specs error: {e}")
            raise
    
    async def update_job_spec(self, job_spec_id: str, update_data: Dict[str, Any]) -> bool:
        """Mock update job spec"""
        try:
            if job_spec_id in self.job_specs:
                self.job_specs[job_spec_id].update(update_data)
                self.job_specs[job_spec_id]["updated_at"] = datetime.utcnow()
                logger.info(f"Mock update job spec: {job_spec_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Mock update job spec error: {e}")
            raise
    
    async def delete_job_spec(self, job_spec_id: str) -> bool:
        """Mock delete job spec"""
        try:
            if job_spec_id in self.job_specs:
                del self.job_specs[job_spec_id]
                logger.info(f"Mock delete job spec: {job_spec_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Mock delete job spec error: {e}")
            raise
    
    # Execution operations
    async def create_execution(self, execution: Any) -> str:
        """Mock create execution"""
        try:
            execution_id = self._generate_id()
            execution_dict = execution.dict(by_alias=True, exclude={"id"})
            execution_dict["_id"] = execution_id
            self.executions[execution_id] = execution_dict
            
            logger.info(f"Mock create execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Mock create execution error: {e}")
            raise
    
    async def get_execution_by_id(self, execution_id: str) -> Optional[Any]:
        """Mock get execution by ID"""
        try:
            if execution_id in self.executions:
                execution_doc = self.executions[execution_id].copy()
                execution_doc["id"] = execution_doc["_id"]
                return execution_doc
            return None
            
        except Exception as e:
            logger.error(f"Mock get execution error: {e}")
            raise
    
    async def list_executions(self, skip: int = 0, limit: int = 20, 
                            job_spec_id: Optional[str] = None,
                            status: Optional[str] = None,
                            started_by: Optional[str] = None,
                            sort_by: str = "created_at", sort_order: int = -1) -> List[Any]:
        """Mock list executions"""
        try:
            executions = []
            for execution_id, execution_doc in self.executions.items():
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
                executions.append(execution_doc)
            
            # Simple sorting
            if sort_by in ["created_at", "updated_at", "started_at"]:
                executions.sort(key=lambda x: x.get(sort_by, ""), reverse=(sort_order == -1))
            
            return executions[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"Mock list executions error: {e}")
            raise
    
    async def count_executions(self, job_spec_id: Optional[str] = None, 
                             status: Optional[str] = None, started_by: Optional[str] = None) -> int:
        """Mock count executions"""
        try:
            count = 0
            for execution_doc in self.executions.values():
                if job_spec_id:
                    if execution_doc.get("job_spec_id") != job_spec_id:
                        continue
                if status:
                    if execution_doc.get("status") != status:
                        continue
                if started_by:
                    if execution_doc.get("started_by") != started_by:
                        continue
                count += 1
            return count
            
        except Exception as e:
            logger.error(f"Mock count executions error: {e}")
            raise
    
    async def update_execution(self, execution_id: str, update_data: Dict[str, Any]) -> bool:
        """Mock update execution"""
        try:
            if execution_id in self.executions:
                self.executions[execution_id].update(update_data)
                self.executions[execution_id]["updated_at"] = datetime.utcnow()
                logger.info(f"Mock update execution: {execution_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Mock update execution error: {e}")
            raise
    
    async def create_execution_history(self, history: Any) -> str:
        """Mock create execution history"""
        try:
            history_id = self._generate_id()
            history_dict = history.dict(by_alias=True, exclude={"id"})
            history_dict["_id"] = history_id
            self.execution_history[history_id] = history_dict
            
            logger.info(f"Mock create execution history: {history_id}")
            return history_id
            
        except Exception as e:
            logger.error(f"Mock create execution history error: {e}")
            raise
    
    async def get_execution_history(self, execution_id: str) -> List[Any]:
        """Mock get execution history"""
        try:
            history = []
            for history_id, history_doc in self.execution_history.items():
                if history_doc.get("execution_id") == execution_id:
                    history_doc = history_doc.copy()
                    history_doc["id"] = history_doc["_id"]
                    history.append(history_doc)
            
            # Sort by performed_at desc
            history.sort(key=lambda x: x.get("performed_at", ""), reverse=True)
            return history
            
        except Exception as e:
            logger.error(f"Mock get execution history error: {e}")
            raise


# Mock instances
mock_minio_service = MockMinIOService()
mock_mongo_service = MockMongoService()
