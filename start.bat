@echo off
echo 🚀 Khởi động Flink Manager API...
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được cài đặt hoặc không có trong PATH
    pause
    exit /b 1
)

REM Kiểm tra virtual environment
if not exist "venv" (
    echo 📦 Tạo virtual environment...
    python -m venv venv
)

REM Kích hoạt virtual environment
echo 🔧 Kích hoạt virtual environment...
call venv\Scripts\activate.bat

REM Cài đặt dependencies
echo 📚 Cài đặt dependencies...
pip install -r requirements.txt

REM Chạy ứng dụng
echo 🚀 Khởi động ứng dụng...
echo 📚 Swagger UI: http://localhost:8000/docs
echo ❤️  Health Check: http://localhost:8000/api/v1/health
echo.

python run.py

pause

