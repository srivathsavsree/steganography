# Deployment Guide

## Prerequisites

- AWS Account with S3 access
- Render.com account
- GitHub repository

## S3 Setup

1. Create an S3 bucket for the application
2. Configure CORS on the S3 bucket:
   ```json
   [
       {
           "AllowedHeaders": ["*"],
           "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
           "AllowedOrigins": [
               "https://steganography-e1l9.onrender.com",
               "https://steganography-api.onrender.com",
               "http://localhost:3000"
           ],
           "ExposeHeaders": ["ETag"],
           "MaxAgeSeconds": 3000
       }
   ]
   ```

## Environment Variables

You need to set up the following environment variables in Render.com:

### Backend Service

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_S3_BUCKET_NAME`: steganography001 (or your bucket name)
- `AWS_S3_REGION`: us-east-1 (or your region)

### Frontend Service

- `NEXT_PUBLIC_API_URL`: https://steganography-api.onrender.com (or your backend URL)

## Deployment Steps

1. Push your code to GitHub
2. Create services on Render.com using the Blueprint or manually:
   - Backend service pointing to the `backend` folder
   - Frontend service pointing to the `frontend` folder
3. Set up environment variables in the Render dashboard
4. Deploy both services

## Security Notes

- Never commit AWS credentials or any secrets to your repository
- Use environment variables for sensitive information
- Regularly rotate your AWS credentials
- Monitor your AWS usage for any unexpected activity
