import boto3
import os
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_S3_REGION", "us-east-1")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def configure_cors():
    """Configure CORS for the S3 bucket."""
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
            'AllowedOrigins': [
                'https://steganography-frontend.onrender.com',
                'https://steganography-e1l9.onrender.com',
                'http://localhost:3000'
            ],
            'ExposeHeaders': ['ETag'],
            'MaxAgeSeconds': 3000
        }]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=AWS_S3_BUCKET,
            CORSConfiguration=cors_configuration
        )
        print(f"CORS configuration updated for bucket: {AWS_S3_BUCKET}")
        return True
    except Exception as e:
        print(f"Error setting CORS configuration: {str(e)}")
        return False

# Call configure_cors on module import
try:
    configure_cors()
except Exception as e:
    print(f"Warning: Could not configure CORS for S3 bucket: {str(e)}")

def upload_file_to_s3(file_path: str, object_name: str = None) -> str:
    if object_name is None:
        object_name = f"stego/{uuid4()}.png"
    s3_client.upload_file(
        file_path, 
        AWS_S3_BUCKET, 
        object_name, 
        ExtraArgs={
            "ContentType": "image/png",
            "ACL": "public-read"  # Make the object publicly readable
        }
    )
    url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
    return url
