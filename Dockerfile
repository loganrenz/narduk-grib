# Multi-stage build for full-stack application

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build the Nuxt application as static site
# Set API base to empty string for same-origin API calls in production
ENV NUXT_PUBLIC_API_BASE=
ENV NODE_ENV=production
RUN npm run generate

# Stage 2: Build backend
FROM python:3.11-slim AS backend-builder

# Install system dependencies required for ecCodes
RUN apt-get update && apt-get install -y \
    libeccodes-dev \
    libeccodes-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final production image
FROM python:3.11-slim

# Install system dependencies required for ecCodes
RUN apt-get update && apt-get install -y \
    libeccodes-dev \
    libeccodes-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application code
COPY backend/ ./

# Copy built frontend static files (Nuxt generate creates .output/public)
COPY --from=frontend-builder /app/frontend/.output/public /app/static

# Create directory for GRIB files
RUN mkdir -p /app/grib_files

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
