import hashlib
import os
from typing import Optional
from datetime import datetime


def calculate_file_hash(file_path: str) -> str:
    """Tính hash SHA256 của file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_bytes_hash(data: bytes) -> str:
    """Tính hash SHA256 của bytes data"""
    return hashlib.sha256(data).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format kích thước file thành string dễ đọc"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_jar_file(file_path: str) -> bool:
    """Kiểm tra file có phải JAR hợp lệ không"""
    try:
        # Kiểm tra extension
        if not file_path.lower().endswith('.jar'):
            return False
        
        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path):
            return False
        
        # Kiểm tra file có phải ZIP file không (JAR là ZIP file)
        import zipfile
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # Kiểm tra có MANIFEST.MF không
            if 'META-INF/MANIFEST.MF' not in zip_file.namelist():
                return False
        
        return True
        
    except Exception:
        return False


def generate_artifact_path(artifact_name: str, version: str) -> str:
    """Tạo đường dẫn artifact trong MinIO"""
    return f"artifacts/{artifact_name}/versions/{version}/fatjar/{artifact_name}-{version}.jar"


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse version string thành tuple (major, minor, patch)"""
    try:
        parts = version.split('.')
        if len(parts) != 3:
            raise ValueError("Version phải có format x.y.z")
        
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        raise ValueError(f"Version không hợp lệ: {version}")


def compare_versions(version1: str, version2: str) -> int:
    """So sánh 2 version strings
    Returns: -1 nếu version1 < version2, 0 nếu bằng, 1 nếu version1 > version2
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)
    
    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


def sanitize_filename(filename: str) -> str:
    """Làm sạch filename để tránh các ký tự không hợp lệ"""
    # Loại bỏ các ký tự không hợp lệ
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Giới hạn độ dài
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def get_current_timestamp() -> str:
    """Lấy timestamp hiện tại dưới dạng ISO string"""
    return datetime.utcnow().isoformat()


def format_duration(seconds: float) -> str:
    """Format thời gian thành string dễ đọc"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

