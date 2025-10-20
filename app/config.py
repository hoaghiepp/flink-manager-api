from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Cấu hình ứng dụng"""
    
    # API Settings
    app_name: str = "Flink Manager API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database Settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "flink_manager"
    
    # MinIO Settings
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "artifacts"
    minio_secure: bool = False
    
    # Flink Settings
    flink_rest_api_url: str = "http://localhost:8081"
    
    # Security Settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
