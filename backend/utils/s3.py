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
    """
    Upload a file to an S3 bucket
    
    :param file_path: File to upload
    :param object_name: S3 object name. If not specified a random UUID is used
    :return: Public URL of the uploaded file
    """
    try:
        # Validate file path
        if not os.path.exists(file_path):
            error_msg = f"File does not exist: {file_path}"
            print(f"[ERROR] {error_msg}")
            raise FileNotFoundError(error_msg)
        
        print(f"[INFO] Uploading file {file_path} to S3")
        print(f"[INFO] File size: {os.path.getsize(file_path)} bytes")
        
        # Set default object name if not provided
        if object_name is None:
            # Determine appropriate file extension based on the source file
            file_ext = os.path.splitext(file_path.lower())[1]
            if not file_ext:
                file_ext = ".bin"  # Default if no extension
            object_name = f"stego/{uuid4()}{file_ext}"
        
        print(f"[INFO] S3 object name: {object_name}")
        print(f"[INFO] S3 bucket: {AWS_S3_BUCKET}")
        
        # Validate AWS credentials and bucket name
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_S3_BUCKET:
            error_msg = "Missing AWS credentials or bucket name"
            print(f"[ERROR] {error_msg}")
            print(f"[DEBUG] AWS_ACCESS_KEY_ID exists: {bool(AWS_ACCESS_KEY_ID)}")
            print(f"[DEBUG] AWS_SECRET_ACCESS_KEY exists: {bool(AWS_SECRET_ACCESS_KEY)}")
            print(f"[DEBUG] AWS_S3_BUCKET exists: {bool(AWS_S3_BUCKET)}")
            raise ValueError(error_msg)
            
        # Determine content type based on file extension
        content_type = "application/octet-stream"  # Default
        file_ext = os.path.splitext(file_path.lower())[1]
        
        if file_ext == ".png" or file_ext == ".jpg" or file_ext == ".jpeg":
            content_type = "image/png" if file_ext == ".png" else "image/jpeg"
        elif file_ext == ".wav":
            content_type = "audio/wav"
        elif file_ext == ".mp3":
            content_type = "audio/mpeg"
        elif file_ext == ".mp4":
            content_type = "video/mp4"
        
        print(f"[INFO] Content type set to: {content_type}")
        
        # Upload the file
        s3_client.upload_file(
            file_path, 
            AWS_S3_BUCKET, 
            object_name, 
            ExtraArgs={
                "ContentType": content_type,
                "ACL": "public-read"  # Make the object publicly readable
            }
        )
        
        # Generate the URL
        url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        print(f"[INFO] Successfully uploaded to S3: {url}")
        
        return url
        
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")
        raise
    except ValueError as e:
        print(f"[ERROR] Value error: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] S3 upload error: {str(e)}")
        print(f"[ERROR] Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise
