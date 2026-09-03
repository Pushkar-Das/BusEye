"""
BusEye — AWS S3 Handler
Uploads detection images to S3, retrieves URLs, lists stored evidence.
"""

import boto3
import os
import io
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class S3Handler:
    def __init__(self):
        self.bucket = os.getenv("AWS_BUCKET_NAME", "buseye-detections")
        self.region = os.getenv("AWS_REGION", "ap-south-1")
        self._connected = False

        try:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            # Quick check: list buckets to verify credentials
            self.s3.head_bucket(Bucket=self.bucket)
            self._connected = True
            print(f"[S3] Connected to bucket: {self.bucket}")
        except NoCredentialsError:
            print("[S3] WARNING: AWS credentials not set. S3 upload disabled.")
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "404":
                print(f"[S3] Bucket '{self.bucket}' not found. Creating...")
                self._create_bucket()
            elif code == "403":
                print(f"[S3] Access denied to bucket '{self.bucket}'. Check IAM permissions.")
            else:
                print(f"[S3] ClientError: {e}")
        except Exception as e:
            print(f"[S3] Connection failed: {e}")

    @property
    def is_connected(self):
        return self._connected

    def _create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            if self.region == "us-east-1":
                self.s3.create_bucket(Bucket=self.bucket)
            else:
                self.s3.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={"LocationConstraint": self.region}
                )
            self._connected = True
            print(f"[S3] Bucket '{self.bucket}' created successfully.")
        except Exception as e:
            print(f"[S3] Could not create bucket: {e}")

    def upload_image(self, image_bytes: bytes, bus_id: str, event_type: str) -> str:
        """
        Upload a detection frame image to S3.
        Returns the public S3 URL, or empty string if upload fails.
        """
        if not self._connected:
            return ""

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{bus_id}_{event_type}_{timestamp}.jpg"
        key = f"detections/{datetime.utcnow().strftime('%Y/%m/%d')}/{filename}"

        try:
            self.s3.upload_fileobj(
                io.BytesIO(image_bytes),
                self.bucket,
                key,
                ExtraArgs={
                    "ContentType": "image/jpeg",
                    "Metadata": {
                        "bus_id": bus_id,
                        "event_type": event_type,
                        "timestamp": timestamp
                    }
                }
            )
            url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
            print(f"[S3] Uploaded: {url}")
            return url
        except ClientError as e:
            print(f"[S3] Upload failed: {e}")
            return ""

    def get_presigned_url(self, s3_key: str, expiry_seconds: int = 3600) -> str:
        """
        Generate a temporary pre-signed URL for a private S3 object.
        Valid for expiry_seconds (default: 1 hour).
        """
        if not self._connected:
            return ""
        try:
            return self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=expiry_seconds
            )
        except ClientError as e:
            print(f"[S3] Presigned URL error: {e}")
            return ""

    def list_recent_images(self, prefix: str = "detections/", limit: int = 50) -> list:
        """
        List recently uploaded detection images from S3.
        Returns list of dicts with key, url, last_modified.
        """
        if not self._connected:
            return []
        try:
            resp = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=limit
            )
            results = []
            for obj in resp.get("Contents", []):
                key = obj["Key"]
                url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
                results.append({
                    "key": key,
                    "url": url,
                    "size_kb": round(obj["Size"] / 1024, 1),
                    "last_modified": obj["LastModified"].isoformat()
                })
            return results
        except ClientError as e:
            print(f"[S3] List error: {e}")
            return []

    def delete_image(self, s3_key: str) -> bool:
        """Delete a single image from S3"""
        if not self._connected:
            return False
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError:
            return False


# Singleton instance
_s3 = None

def get_s3() -> S3Handler:
    global _s3
    if _s3 is None:
        _s3 = S3Handler()
    return _s3
