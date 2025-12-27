# ═══════════════════════════════════════════════════════════════════════════════
# إدارة التخزين S3/MinIO لنظام mkh_Manus
# يوفر رفع وتنزيل وإدارة المرفقات
# التاريخ: ديسمبر 2025
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import mimetypes

from minio import Minio
from minio.error import S3Error
from .logging_config import get_logger

logger = get_logger(__name__)

# ═══ Configuration ═══
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "mkh-attachments")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# ═══ MinIO Client ═══
_minio_client: Optional[Minio] = None

def get_minio_client() -> Minio:
    """الحصول على عميل MinIO (Singleton)"""
    global _minio_client
    
    if _minio_client is None:
        try:
            _minio_client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )
            logger.info(f"MinIO client initialized: {MINIO_ENDPOINT}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise
    
    return _minio_client

def ensure_bucket_exists(bucket_name: str = MINIO_BUCKET) -> None:
    """التأكد من وجود Bucket"""
    try:
        client = get_minio_client()
        
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"Bucket created: {bucket_name}")
        else:
            logger.debug(f"Bucket already exists: {bucket_name}")
            
    except S3Error as e:
        logger.error(f"Failed to ensure bucket exists: {e}")
        raise

# ═══ Upload Operations ═══
def upload_file(
    file_path: str,
    object_name: Optional[str] = None,
    content_type: Optional[str] = None,
    bucket_name: str = MINIO_BUCKET
) -> Dict[str, Any]:
    """
    رفع ملف إلى MinIO/S3
    
    Args:
        file_path: مسار الملف المحلي
        object_name: اسم الكائن في S3 (اختياري)
        content_type: نوع المحتوى (اختياري)
        bucket_name: اسم Bucket
    
    Returns:
        معلومات الملف المرفوع
    """
    try:
        ensure_bucket_exists(bucket_name)
        client = get_minio_client()
        
        # تحديد اسم الكائن
        if object_name is None:
            object_name = Path(file_path).name
        
        # تحديد نوع المحتوى
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = "application/octet-stream"
        
        # الحصول على حجم الملف
        file_size = os.path.getsize(file_path)
        
        # رفع الملف
        with open(file_path, "rb") as file_data:
            client.put_object(
                bucket_name,
                object_name,
                file_data,
                file_size,
                content_type=content_type
            )
        
        logger.info(f"File uploaded: {object_name} ({file_size} bytes)")
        
        # إنشاء signed URL
        url = get_presigned_url(object_name, bucket_name, expires_hours=24)
        
        return {
            "bucket": bucket_name,
            "key": object_name,
            "size": file_size,
            "content_type": content_type,
            "url": url,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to upload file {file_path}: {e}")
        raise

def upload_bytes(
    data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
    bucket_name: str = MINIO_BUCKET
) -> Dict[str, Any]:
    """
    رفع بيانات bytes إلى MinIO/S3
    
    Args:
        data: البيانات
        object_name: اسم الكائن
        content_type: نوع المحتوى
        bucket_name: اسم Bucket
    
    Returns:
        معلومات الملف المرفوع
    """
    try:
        ensure_bucket_exists(bucket_name)
        client = get_minio_client()
        
        from io import BytesIO
        
        data_stream = BytesIO(data)
        data_size = len(data)
        
        client.put_object(
            bucket_name,
            object_name,
            data_stream,
            data_size,
            content_type=content_type
        )
        
        logger.info(f"Bytes uploaded: {object_name} ({data_size} bytes)")
        
        url = get_presigned_url(object_name, bucket_name, expires_hours=24)
        
        return {
            "bucket": bucket_name,
            "key": object_name,
            "size": data_size,
            "content_type": content_type,
            "url": url,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to upload bytes {object_name}: {e}")
        raise

# ═══ Download Operations ═══
def download_file(
    object_name: str,
    destination_path: str,
    bucket_name: str = MINIO_BUCKET
) -> str:
    """
    تنزيل ملف من MinIO/S3
    
    Args:
        object_name: اسم الكائن
        destination_path: مسار الحفظ المحلي
        bucket_name: اسم Bucket
    
    Returns:
        مسار الملف المحلي
    """
    try:
        client = get_minio_client()
        
        client.fget_object(bucket_name, object_name, destination_path)
        
        logger.info(f"File downloaded: {object_name} -> {destination_path}")
        return destination_path
        
    except Exception as e:
        logger.error(f"Failed to download file {object_name}: {e}")
        raise

def download_file_to_tmp(
    object_name: str,
    bucket_name: str = MINIO_BUCKET
) -> str:
    """
    تحميل ملف إلى مجلد مؤقت
    
    Args:
        object_name: اسم الكائن
        bucket_name: اسم Bucket
    
    Returns:
        مسار الملف المؤقت
    """
    try:
        import tempfile
        
        # إنشاء ملف مؤقت
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(object_name).suffix)
        temp_path = temp_file.name
        temp_file.close()
        
        # تنزيل الملف
        download_file(object_name, temp_path, bucket_name)
        
        logger.info(f"File downloaded to tmp: {object_name} -> {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Failed to download file to tmp {object_name}: {e}")
        raise

def get_object_bytes(
    object_name: str,
    bucket_name: str = MINIO_BUCKET
) -> bytes:
    """
    الحصول على محتوى كائن كـ bytes
    
    Args:
        object_name: اسم الكائن
        bucket_name: اسم Bucket
    
    Returns:
        محتوى الملف
    """
    try:
        client = get_minio_client()
        
        response = client.get_object(bucket_name, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        
        logger.info(f"Object bytes retrieved: {object_name} ({len(data)} bytes)")
        return data
        
    except Exception as e:
        logger.error(f"Failed to get object bytes {object_name}: {e}")
        raise

# ═══ URL Operations ═══
def get_presigned_url(
    object_name: str,
    bucket_name: str = MINIO_BUCKET,
    expires_hours: int = 24
) -> str:
    """
    إنشاء signed URL للوصول المؤقت
    
    Args:
        object_name: اسم الكائن
        bucket_name: اسم Bucket
        expires_hours: مدة الصلاحية بالساعات
    
    Returns:
        Signed URL
    """
    try:
        client = get_minio_client()
        
        url = client.presigned_get_object(
            bucket_name,
            object_name,
            expires=timedelta(hours=expires_hours)
        )
        
        logger.debug(f"Presigned URL generated: {object_name}")
        return url
        
    except Exception as e:
        logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
        raise

def get_presigned_upload_url(
    object_name: str,
    bucket_name: str = MINIO_BUCKET,
    expires_hours: int = 1
) -> str:
    """
    إنشاء signed URL للرفع المباشر
    
    Args:
        object_name: اسم الكائن
        bucket_name: اسم Bucket
        expires_hours: مدة الصلاحية بالساعات
    
    Returns:
        Signed URL للرفع
    """
    try:
        client = get_minio_client()
        
        url = client.presigned_put_object(
            bucket_name,
            object_name,
            expires=timedelta(hours=expires_hours)
        )
        
        logger.debug(f"Presigned upload URL generated: {object_name}")
        return url
        
    except Exception as e:
        logger.error(f"Failed to generate presigned upload URL for {object_name}: {e}")
        raise

# ═══ Management Operations ═══
def delete_object(
    object_name: str,
    bucket_name: str = MINIO_BUCKET
) -> None:
    """
    حذف كائن من MinIO/S3
    
    Args:
        object_name: اسم الكائن
        bucket_name: اسم Bucket
    """
    try:
        client = get_minio_client()
        
        client.remove_object(bucket_name, object_name)
        
        logger.info(f"Object deleted: {object_name}")
        
    except Exception as e:
        logger.error(f"Failed to delete object {object_name}: {e}")
        raise

def list_objects(
    prefix: Optional[str] = None,
    bucket_name: str = MINIO_BUCKET
) -> List[Dict[str, Any]]:
    """
    سرد الكائنات في Bucket
    
    Args:
        prefix: بادئة للتصفية (اختياري)
        bucket_name: اسم Bucket
    
    Returns:
        قائمة الكائنات
    """
    try:
        client = get_minio_client()
        
        objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
        
        result = []
        for obj in objects:
            result.append({
                "name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                "etag": obj.etag,
            })
        
        logger.info(f"Listed {len(result)} objects from {bucket_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to list objects: {e}")
        raise

def get_object_info(
    object_name: str,
    bucket_name: str = MINIO_BUCKET
) -> Dict[str, Any]:
    """
    الحصول على معلومات كائن
    
    Args:
        object_name: اسم الكائن
        bucket_name: اسم Bucket
    
    Returns:
        معلومات الكائن
    """
    try:
        client = get_minio_client()
        
        stat = client.stat_object(bucket_name, object_name)
        
        return {
            "name": stat.object_name,
            "size": stat.size,
            "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
            "etag": stat.etag,
            "content_type": stat.content_type,
            "metadata": stat.metadata,
        }
        
    except Exception as e:
        logger.error(f"Failed to get object info {object_name}: {e}")
        raise

# ═══ Cleanup Operations ═══
def move_to_quarantine(
    object_name: str,
    bucket_name: str = MINIO_BUCKET,
    quarantine_bucket: str = "mkh-quarantine"
) -> None:
    """
    نقل ملف إلى الحجر الصحي
    
    Args:
        object_name: اسم الكائن
        bucket_name: اسم Bucket الأصلي
        quarantine_bucket: اسم Bucket الحجر الصحي
    """
    try:
        client = get_minio_client()
        
        # التأكد من وجود bucket الحجر الصحي
        ensure_bucket_exists(quarantine_bucket)
        
        # نسخ الملف إلى الحجر الصحي
        from minio.commonconfig import CopySource
        
        client.copy_object(
            quarantine_bucket,
            object_name,
            CopySource(bucket_name, object_name)
        )
        
        # حذف الملف الأصلي
        delete_object(object_name, bucket_name)
        
        logger.info(f"File moved to quarantine: {object_name}")
        
    except Exception as e:
        logger.error(f"Failed to move file to quarantine {object_name}: {e}")
        raise

def cleanup_expired_attachments() -> int:
    """
    تنظيف المرفقات المنتهية
    
    Returns:
        عدد المرفقات المحذوفة
    """
    try:
        from . import db
        
        # الحصول على المرفقات المنتهية من قاعدة البيانات
        expired_attachments = db.get_expired_attachments()
        
        deleted_count = 0
        for attachment in expired_attachments:
            try:
                delete_object(attachment["storage_key"], attachment["storage_bucket"])
                db.delete_attachment(attachment["id"])
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete expired attachment {attachment['id']}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} expired attachments")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired attachments: {e}")
        raise

# ═══ Health Check ═══
def check_storage_health() -> bool:
    """
    فحص صحة التخزين
    
    Returns:
        True إذا كان التخزين يعمل بشكل صحيح
    """
    try:
        client = get_minio_client()
        
        # محاولة سرد Buckets
        buckets = client.list_buckets()
        
        # التأكد من وجود Bucket الرئيسي
        bucket_exists = any(b.name == MINIO_BUCKET for b in buckets)
        
        if not bucket_exists:
            logger.warning(f"Main bucket {MINIO_BUCKET} does not exist")
            ensure_bucket_exists()
        
        return True
        
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return False
