from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import logging
import time

from app.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.exceptions import handle_exception
from app.api.v1 import artifacts, jobs, health

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Tạo FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Flink Manager API
    
    API để quản lý Flink jobs với các tính năng:
    
    * **Artifacts**: Upload, quản lý và versioning JAR files
    * **Job Configs**: Tạo và quản lý cấu hình jobs
    * **Deployment**: Deploy và quản lý jobs trên Flink cluster
    * **Audit**: Theo dõi lịch sử deployment và thay đổi
    
    ### Kiến trúc
    
    - **MinIO**: Lưu trữ JAR artifacts
    - **MongoDB**: Lưu trữ metadata và job configs
    - **Flink REST API**: Tương tác với Flink cluster
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên cấu hình cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware để log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Lỗi hệ thống không mong muốn",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


# Startup và shutdown events
@app.on_event("startup")
async def startup_event():
    """Khởi tạo ứng dụng"""
    logger.info("Đang khởi động Flink Manager API...")
    
    try:
        await connect_to_mongo()
        logger.info("Flink Manager API đã sẵn sàng!")
    except Exception as e:
        logger.error(f"Lỗi khởi động: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Dọn dẹp khi tắt ứng dụng"""
    logger.info("Đang tắt Flink Manager API...")
    await close_mongo_connection()
    logger.info("Flink Manager API đã tắt!")


# Include routers
app.include_router(artifacts.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Thông tin về API
    """
    return {
        "message": "Flink Manager API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
    )
    
    # Thêm thông tin server
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
    
    # Thêm tags metadata
    openapi_schema["tags"] = [
        {
            "name": "Artifacts",
            "description": "Quản lý JAR artifacts và metadata"
        },
        {
            "name": "Job Configs", 
            "description": "Quản lý cấu hình jobs và deployment"
        },
        {
            "name": "Health Check",
            "description": "Kiểm tra trạng thái hệ thống"
        },
        {
            "name": "Root",
            "description": "Thông tin cơ bản về API"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )

