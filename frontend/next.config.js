/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  // Explicitly set the environment variables for production build
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://steganography-e1l9.onrender.com',
  },
  // Explicitly allow images from the API domain
  images: {
    domains: ['steganography001.s3.us-east-1.amazonaws.com', 'steganography-e1l9.onrender.com'],
  },
}

module.exports = nextConfig
