# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Create necessary directories if they don't exist
RUN mkdir -p public styles
# Create .env.production if it doesn't exist
RUN if [ ! -f .env.production ]; then \
    echo "NEXT_PUBLIC_API_URL=https://steganography-api.onrender.com" > .env.production; \
    fi
RUN npm run build

# Stage 2: Production image
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next .next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
# Only copy styles directory if it exists
RUN mkdir -p styles
COPY --from=builder /app/styles ./styles
# Create .env file with environment variables
RUN echo "NEXT_PUBLIC_API_URL=https://steganography-api.onrender.com" > .env.production
EXPOSE 3000
CMD ["npm", "start"]
