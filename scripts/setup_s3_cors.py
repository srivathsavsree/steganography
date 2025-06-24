import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS credentials and config
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_S3_REGION", "us-east-1")

def setup_s3_cors():
    """
    Sets up CORS configuration for the S3 bucket
    """
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET]):
        print("Error: AWS credentials or bucket name not found in environment variables.")
        print("Make sure you have set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_S3_BUCKET_NAME.")
        return False

    try:
        # Create S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

        # Define CORS configuration
        cors_configuration = {
            "CORSRules": [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
                    "AllowedOrigins": [
                        "https://steganography-frontend.onrender.com",
                        "https://steganography-api.onrender.com",
                        "http://localhost:3000"
                    ],
                    "ExposeHeaders": ["ETag"],
                    "MaxAgeSeconds": 3000
                }
            ]
        }

        # Set the CORS configuration
        s3_client.put_bucket_cors(
            Bucket=AWS_S3_BUCKET,
            CORSConfiguration=cors_configuration
        )

        print(f"✅ CORS configuration successfully updated for bucket: {AWS_S3_BUCKET}")
        print("Allowed origins:")
        for origin in cors_configuration["CORSRules"][0]["AllowedOrigins"]:
            print(f"  - {origin}")
        return True

    except Exception as e:
        print(f"❌ Error setting CORS configuration: {str(e)}")
        return False

if __name__ == "__main__":
    print("Setting up CORS configuration for S3 bucket...")
    setup_s3_cors()
