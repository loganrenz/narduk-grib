FROM python:3.11-slim

# Install system dependencies required for ecCodes
RUN apt-get update && apt-get install -y \
    libeccodes-dev \
    libeccodes-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for GRIB files
RUN mkdir -p /app/grib_files

# Expose port (Coolify will automatically assign and set PORT env var)
# Using 8000 as default, but app will use PORT env var if set by Coolify
EXPOSE 8000

# Run the application - use PORT env var if provided (Coolify), otherwise default to 8000
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
