# Flink Manager API

API hiện đại để quản lý Flink jobs với tính năng versioning, audit và traceability.

## 🚀 Tính năng chính

- **Artifact Management**: Upload, quản lý và versioning JAR files
- **Job Configuration**: Tạo và quản lý cấu hình jobs
- **Deployment**: Deploy và quản lý jobs trên Flink cluster
- **Audit & Traceability**: Theo dõi lịch sử deployment và thay đổi
- **RESTful API**: API thống nhất với Swagger documentation
- **Health Monitoring**: Kiểm tra trạng thái hệ thống và dependencies

## 🏗️ Kiến trúc

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Developer     │    │   CI/CD         │    │   Flink Manager │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │     Git     │ │    │ │   Pipeline  │ │    │ │  API Layer  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    │                 │
         │                       │            │ ┌─────────────┐ │
         │                       │            │ │   MinIO     │ │
         │                       │            │ │ (Artifacts) │ │
         │                       │            │ └─────────────┘ │
         │                       │            │                 │
         │                       │            │ ┌─────────────┐ │
         │                       │            │ │   MongoDB   │ │
         │                       │            │ │  (Catalog)  │ │
         │                       │            │ └─────────────┘ │
         │                       │            └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Flink Cluster   │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │ Flink Jobs  │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

## 📋 Yêu cầu hệ thống

- Python 3.8+
- MongoDB 4.4+
- MinIO Server
- Flink Cluster với REST API

## 🛠️ Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd FlinkManager
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment

```bash
cp env.example .env
# Chỉnh sửa .env theo môi trường của bạn
```

### 5. Khởi động services

```bash
# MongoDB
mongod

# MinIO
minio server /data --console-address ":9001"

# Flink Cluster
./bin/start-cluster.sh
```

### 6. Chạy ứng dụng

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Sau khi khởi động ứng dụng, truy cập:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔧 Cấu hình

### Environment Variables

| Variable | Mô tả | Mặc định |
|----------|-------|----------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `flink_manager` |
| `MINIO_ENDPOINT` | MinIO server endpoint | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |
| `MINIO_BUCKET` | MinIO bucket name | `artifacts` |
| `FLINK_REST_API_URL` | Flink REST API URL | `http://localhost:8081` |

### Cấu trúc lưu trữ MinIO

```
artifacts/
  <artifact-name>/
    versions/
      <version>/
        fatjar/
          <artifact-name>-<version>.jar
        metadata.json
```

## 📖 Sử dụng API

### 0. Run local

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 1. Upload Artifact

```bash
curl -X POST "http://localhost:8000/api/v1/artifacts/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@my-job.jar" \
  -F 'metadata={"artifact_name": "my-job", "version": "1.0.0", "entry_classes": ["com.example.MyJob"], "uploaded_by": "developer"}'
```

### 2. Tạo Job Config

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "my-job-config",
    "artifact_id": "artifact_id_here",
    "entry_class": "com.example.MyJob",
    "parallelism": 2,
    "program_args": ["--input", "hdfs://input", "--output", "hdfs://output"],
    "created_by": "developer"
  }'
```

### 3. Deploy Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/{job_id}/deploy" \
  -H "Content-Type: application/json" \
  -d '{"deployed_by": "developer"}'
```

### 4. Stop Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/{job_id}/stop" \
  -H "Content-Type: application/json" \
  -d '{"savepoint": true, "savepoint_path": "hdfs://savepoints/"}'
```

## 🔍 Monitoring

### Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "mongodb": "healthy",
    "minio": "healthy",
    "flink_cluster": "healthy"
  }
}
```

## 🧪 Testing

```bash
# Chạy tests
pytest

# Với coverage
pytest --cov=app tests/
```

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t flink-manager-api .

# Run container
docker run -p 8000:8000 --env-file .env flink-manager-api
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - mongo
      - minio
  
  mongo:
    image: mongo:4.4
    ports:
      - "27017:27017"
  
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    command: server /data --console-address ":9001"
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Documentation: [Wiki](https://github.com/your-repo/wiki)

