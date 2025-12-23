from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

router = APIRouter(tags=["storage"])

MINIO_ENDPOINT = "http://s3.healthy.local"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "healthy-menu-dishes"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


class PresignRequest(BaseModel):
    dish_id: int
    filename: str


@router.post("/presign-upload/")
async def presign_upload(req: PresignRequest):
    try:
        ext = req.filename.split(".")[-1].lower()
        key = f"dishes/{req.dish_id}/original.{ext}"

        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": MINIO_BUCKET,
                "Key": key,
                "ContentType": "image/jpeg",
            },
            ExpiresIn=900,
            HttpMethod="PUT",
        )

        public_url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{key}"

        return {
            "upload_url": url,
            "public_url": public_url,
            "key": key,
        }

    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

