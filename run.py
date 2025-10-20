#!/usr/bin/env python3
"""
Script để chạy Flink Manager API
"""

import uvicorn
import os
import sys
from pathlib import Path

# Thêm app directory vào Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

if __name__ == "__main__":
    # Cấu hình từ environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"🚀 Khởi động Flink Manager API...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"📊 Log Level: {log_level}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"❤️  Health: http://{host}:{port}/api/v1/health")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )

