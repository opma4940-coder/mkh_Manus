"""
مسارات رفع الملفات (Uploads Routes)
يوفر endpoints لطلب روابط رفع موقعة مؤقتة (Presigned URLs) وتأكيد الرفع
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import boto3
import os
import time
import uuid
from typing import Optional

router = APIRouter()


class UploadRequest(BaseModel):
    """نموذج طلب رفع ملف"""
    filename: str
    content_type: str
    size: int
    task_id: Optional[str] = None


class UploadCallback(BaseModel):
    """نموذج تأكيد رفع الملف"""
    object_key: str
    task_id: Optional[str] = None


@router.post("/uploads/request")
def request_upload(body: UploadRequest):
    """
    طلب رابط رفع موقع مؤقت (Presigned URL)
    
    يقوم بإنشاء رابط آمن لرفع الملف مباشرة إلى S3/MinIO
    دون المرور عبر الخادم الخلفي
    """
    try:
        # إنشاء عميل S3
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", os.getenv("AWS_ACCESS_KEY_ID")),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", os.getenv("AWS_SECRET_ACCESS_KEY")),
            endpoint_url=os.getenv("S3_ENDPOINT", os.getenv("MINIO_ENDPOINT"))
        )
        
        bucket = os.getenv("S3_BUCKET", os.getenv("MINIO_BUCKET", "mkh-attachments"))
        
        # إنشاء مفتاح فريد للملف
        file_id = str(uuid.uuid4())
        object_key = f"uploads/{int(time.time())}_{file_id}_{body.filename}"
        
        # مدة صلاحية الرابط (15 دقيقة)
        expires_in = 900
        
        # إنشاء رابط رفع موقع
        upload_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key': object_key,
                'ContentType': body.content_type
            },
            ExpiresIn=expires_in
        )
        
        return {
            "upload_url": upload_url,
            "object_key": object_key,
            "expires_in": expires_in,
            "file_id": file_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل إنشاء رابط الرفع: {str(e)}")


@router.post("/uploads/callback")
def upload_callback(body: UploadCallback):
    """
    تأكيد رفع الملف
    
    يتم استدعاؤه بعد نجاح رفع الملف لتسجيل المعلومات في قاعدة البيانات
    """
    try:
        # هنا يتم تسجيل معلومات الملف في قاعدة البيانات
        # يمكن إضافة فحص أمني للملف هنا
        
        return {
            "status": "success",
            "message": "تم تأكيد رفع الملف بنجاح",
            "object_key": body.object_key,
            "file_reference": body.object_key
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل تأكيد رفع الملف: {str(e)}")


@router.get("/uploads/{object_key}/download")
def get_download_url(object_key: str):
    """
    الحصول على رابط تحميل موقع مؤقت
    
    يقوم بإنشاء رابط آمن لتحميل الملف
    """
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", os.getenv("AWS_ACCESS_KEY_ID")),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", os.getenv("AWS_SECRET_ACCESS_KEY")),
            endpoint_url=os.getenv("S3_ENDPOINT", os.getenv("MINIO_ENDPOINT"))
        )
        
        bucket = os.getenv("S3_BUCKET", os.getenv("MINIO_BUCKET", "mkh-attachments"))
        
        # مدة صلاحية الرابط (1 ساعة)
        expires_in = 3600
        
        # إنشاء رابط تحميل موقع
        download_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': object_key
            },
            ExpiresIn=expires_in
        )
        
        return {
            "download_url": download_url,
            "expires_in": expires_in
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل إنشاء رابط التحميل: {str(e)}")
