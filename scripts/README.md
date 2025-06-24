# S3 Configuration Scripts

This directory contains helper scripts for configuring your AWS S3 bucket for the steganography application.

## Available Scripts

### Setup S3 CORS Configuration

```bash
python scripts/setup_s3_cors.py
```

This script sets up the CORS configuration for your S3 bucket to allow requests from:
- https://steganography-frontend.onrender.com
- https://steganography-api.onrender.com
- http://localhost:3000

### Setup S3 Public Access Policy

```bash
python scripts/setup_s3_public_access.py
```

This script sets up a bucket policy to allow public read access for objects in your S3 bucket.

## Environment Variables

Both scripts require the following environment variables to be set:
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key  
- `AWS_S3_BUCKET_NAME`: Your S3 bucket name
- `AWS_S3_REGION` (optional, defaults to 'us-east-1'): The AWS region where your bucket is located

You can set these variables in a `.env` file at the root of your project.
