from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


db = Database()


async def connect_to_mongo():
    """Kết nối đến MongoDB"""
    try:
        # Sử dụng mock mode nếu không có MongoDB
        logger.info("Sử dụng mock database mode")
        return
        
        # Code thực tế cho MongoDB (commented out)
        # db.client = AsyncIOMotorClient(settings.mongodb_url)
        # db.database = db.client[settings.mongodb_database]
        # 
        # # Test connection
        # await db.client.admin.command('ping')
        # logger.info("Kết nối MongoDB thành công")
        # 
        # # Tạo indexes
        # await create_indexes()
        
    except Exception as e:
        logger.warning(f"Sử dụng mock database: {e}")
        pass


async def close_mongo_connection():
    """Đóng kết nối MongoDB"""
    if db.client:
        db.client.close()
        logger.info("Đã đóng kết nối MongoDB")


async def create_indexes():
    """Tạo các index cần thiết"""
    try:
        # Index cho artifacts collection
        await db.database.artifacts.create_index("artifact_name")
        await db.database.artifacts.create_index("version")
        await db.database.artifacts.create_index([("artifact_name", 1), ("version", 1)], unique=True)
        
        # Index cho job_configs collection
        await db.database.job_configs.create_index("job_name", unique=True)
        await db.database.job_configs.create_index("artifact_id")
        await db.database.job_configs.create_index("status")
        await db.database.job_configs.create_index("created_by")
        
        # Index cho deployment_history collection
        await db.database.deployment_history.create_index("job_id")
        await db.database.deployment_history.create_index("deployed_at")
        
        logger.info("Đã tạo các index thành công")
        
    except Exception as e:
        logger.error(f"Lỗi tạo index: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Lấy database instance"""
    return db.database

