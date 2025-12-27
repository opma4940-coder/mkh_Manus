from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3, os, time

router = APIRouter()

class UploadRequest(BaseModel):
    filename: str
    content_type: str
    size: int
    task_id: str = None

@router.post("/uploads/request")
def request_upload(body: UploadRequest):
    s3 = boto3.client("s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT", None))
    bucket = os.getenv("S3_BUCKET")
    object_key = f"uploads/{int(time.time())}_{body.filename}"
    expires_in = 900
    upload_url = s3.generate_presigned_url('put_object', Params={'Bucket': bucket, 'Key': object_key, 'ContentType': body.content_type}, ExpiresIn=expires_in)
    return {"upload_url": upload_url, "object_key": object_key, "expires_in": expires_in}
