# Steganography Web Application

A full-stack web application for hiding and retrieving data within media files (images, audio, video, and files).

## Features

- **Image Steganography**: Hide text messages within PNG images
- **Audio Steganography**: Conceal messages in audio files
- **File-in-Image Steganography**: Embed any file within a PNG image
- **Video Steganography**: Hide messages within video files

## Security Note

This application requires AWS credentials for S3 storage functionality. Never commit these credentials to your repository. Instead:

1. Use `.env` files locally that are excluded from git
2. Set environment variables in your deployment platform (Render.com)
3. See `DEPLOYMENT.md` for secure deployment instructions

## Technology Stack

- **Frontend**: Next.js (React)
- **Backend**: FastAPI (Python)
- **Storage**: AWS S3
- **Containerization**: Docker & Docker Compose

## Setup & Installation

### Prerequisites
- Docker and Docker Compose
- AWS S3 Bucket (for file storage)

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/steganography.git
cd steganography
```

2. Create a `.env` file in the root directory with your AWS credentials:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
AWS_REGION=your_region
```

### Running with Docker

Build and run the application using Docker Compose:
```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Setup

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

## Deploying to Production

For production deployment:
1. Ensure all environment variables are properly set
2. Use the Docker Compose setup with proper domain configuration
3. Consider adding SSL/TLS for HTTPS

## License

[MIT License](LICENSE)
