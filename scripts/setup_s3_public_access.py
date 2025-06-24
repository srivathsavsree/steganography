import boto3
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS credentials and config
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_S3_REGION", "us-east-1")

def setup_s3_public_access():
    """
    Sets up a bucket policy to allow public read access for objects in the S3 bucket
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

        # Define bucket policy to allow public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadForGetBucketObjects",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{AWS_S3_BUCKET}/*"
                }
            ]
        }

        # Convert the policy to JSON
        bucket_policy_string = json.dumps(bucket_policy)

        # Set the bucket policy
        s3_client.put_bucket_policy(
            Bucket=AWS_S3_BUCKET,
            Policy=bucket_policy_string
        )

        print(f"✅ Public access policy successfully set for bucket: {AWS_S3_BUCKET}")
        return True

    except Exception as e:
        print(f"❌ Error setting bucket policy: {str(e)}")
        return False

if __name__ == "__main__":
    print("Setting up public access policy for S3 bucket...")
    setup_s3_public_access()
