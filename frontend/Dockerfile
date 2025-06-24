# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Create necessary directories if they don't exist
RUN mkdir -p public styles
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
COPY --from=builder /app/.env.production ./.env.production
EXPOSE 3000
CMD ["npm", "start"]
