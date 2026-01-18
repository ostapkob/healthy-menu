import os
import boto3
from botocore.client import Config

MINIO_HOST = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT = os.getenv("MINIO_PORT", "9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "ostapkob")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "superpass123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "healthy-menu-dishes")

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_HOST}:{MINIO_PORT}",
    aws_access_key_id=MINIO_ROOT_USER,
    aws_secret_access_key=MINIO_ROOT_PASSWORD,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)

# создаём bucket один раз при импорте
try:
    s3.head_bucket(Bucket=MINIO_BUCKET)
except s3.exceptions.NoSuchBucket:
    s3.create_bucket(Bucket=MINIO_BUCKET)

