import os
import boto3
from botocore.client import Config

MINIO_HOST = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT = os.getenv("MINIO_PORT", "9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "healthy-menu-dishes"

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_HOST}:{MINIO_PORT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)

# создаём bucket один раз при импорте
try:
    s3.head_bucket(Bucket=BUCKET_NAME)
except s3.exceptions.NoSuchBucket:
    s3.create_bucket(Bucket=BUCKET_NAME)

