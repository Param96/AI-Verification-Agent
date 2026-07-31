import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


class StorageManager:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.MINIO_SERVER}",
            aws_access_key_id=settings.MINIO_ROOT_USER,
            aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
            config=boto3.session.Config(signature_version="s3v4"),
        )
        self.bucket_name = "verify-documents"
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.s3_client.create_bucket(Bucket=self.bucket_name)

    def upload_file(self, file_obj, filename: str) -> str:
        s3_path = f"uploads/{filename}"
        self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_path)
        return s3_path

    def get_presigned_url(self, s3_path: str, expiration=3600) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_path},
            ExpiresIn=expiration,
        )


storage = StorageManager()
