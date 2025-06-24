import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_S3_REGION", "us-east-1")

def setup_s3_cors():
    """
    Set up CORS configuration for the S3 bucket
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    
    # CORS configuration to allow all origins (you can restrict to your specific domains in production)
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
            'AllowedOrigins': [
                'http://localhost:3000',
                'https://steganography-frontend.onrender.com',
                # Add any other origins that need to access your S3 bucket
            ],
            'ExposeHeaders': ['ETag', 'x-amz-server-side-encryption'],
            'MaxAgeSeconds': 3000
        }]
    }
    
    # Set the bucket policy to allow public read access
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{AWS_S3_BUCKET}/*"
            }
        ]
    }
    
    try:
        # Apply CORS configuration
        s3_client.put_bucket_cors(
            Bucket=AWS_S3_BUCKET,
            CORSConfiguration=cors_configuration
        )
        print(f"✅ CORS configuration updated for bucket: {AWS_S3_BUCKET}")
        
        # Apply bucket policy for public read access
        import json
        s3_client.put_bucket_policy(
            Bucket=AWS_S3_BUCKET,
            Policy=json.dumps(bucket_policy)
        )
        print(f"✅ Bucket policy updated for public read access on bucket: {AWS_S3_BUCKET}")
        
        # Get and display current CORS configuration
        cors_response = s3_client.get_bucket_cors(Bucket=AWS_S3_BUCKET)
        print("\nCurrent CORS Configuration:")
        print(json.dumps(cors_response, indent=2))
        
        return True
    except Exception as e:
        print(f"❌ Error setting up S3 configuration: {str(e)}")
        return False

if __name__ == "__main__":
    print("Setting up S3 CORS configuration...")
    setup_s3_cors()
