# Steganography Frontend

This is the frontend for the Steganography Web Application, built with Next.js.

## Features

- Image Steganography - Hide text messages in images
- Audio Steganography - Hide messages in audio files
- File-in-Image Steganography - Hide files within images
- Video Steganography - Hide messages in video files

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

## Production

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

Create a `.env.local` file for local development:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, the environment variables are set in the hosting platform (Render.com).
