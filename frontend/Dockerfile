FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Set API base - set BACKEND_URL in Coolify environment variables
# This will be passed as BUILD_ARG_API_BASE build arg
# Defaults to http://localhost:8000 for local development
ARG BUILD_ARG_API_BASE=http://localhost:8000
ENV NUXT_PUBLIC_API_BASE=${BUILD_ARG_API_BASE}
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy built application from builder
COPY --from=builder /app/.output /app/.output
COPY --from=builder /app/package*.json ./

# Expose port
EXPOSE 3000

# Set environment to production
ENV NODE_ENV=production
# Force port 3000 (Coolify may set PORT env var, but Nuxt server should use 3000)
ENV PORT=3000
ENV NITRO_PORT=3000
ENV NITRO_HOST=0.0.0.0

# Run the application
CMD ["node", ".output/server/index.mjs"]
