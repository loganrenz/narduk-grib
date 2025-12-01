# Deployment Guide

This guide covers different deployment options for the GRIB Viewer application.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Manual Deployment](#manual-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Configuration](#configuration)

## Docker Deployment

The easiest way to deploy the application is using Docker and Docker Compose.

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd narduk-grib
```

2. Build and start the services:
```bash
docker-compose up -d
```

This will:
- Build the backend and frontend Docker images
- Start both services
- Create a persistent volume for GRIB files
- Expose backend on port 8000 and frontend on port 3000

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

4. Stop the services:
```bash
docker-compose down
```

5. Stop and remove volumes:
```bash
docker-compose down -v
```

### Custom Configuration

Edit `docker-compose.yml` to customize:
- Port mappings
- Environment variables
- Volume mounts

## Manual Deployment

### Backend Deployment

#### Prerequisites
- Python 3.8+
- ECMWF ecCodes library

#### Install ecCodes

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libeccodes-dev libeccodes-tools
```

**macOS:**
```bash
brew install eccodes
```

**Other systems:**
See [ecCodes installation guide](https://confluence.ecmwf.int/display/ECC/ecCodes+installation)

#### Deploy Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with production settings
```

5. Start the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

For production, use a process manager like systemd, supervisor, or PM2.

#### Example systemd service

Create `/etc/systemd/system/grib-backend.service`:

```ini
[Unit]
Description=GRIB Viewer Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/narduk-grib/backend
Environment="PATH=/path/to/narduk-grib/backend/venv/bin"
ExecStart=/path/to/narduk-grib/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable grib-backend
sudo systemctl start grib-backend
```

### Frontend Deployment

#### Prerequisites
- Node.js 18+

#### Deploy Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with production API URL
```

4. Build for production:
```bash
npm run build
```

5. Start the production server:
```bash
npm run preview
```

For production, consider using:
- Node.js process manager (PM2)
- Nginx as reverse proxy
- Static hosting (Vercel, Netlify, etc.)

#### Example PM2 deployment

```bash
# Install PM2
npm install -g pm2

# Start the app
pm2 start npm --name "grib-frontend" -- run preview

# Save PM2 configuration
pm2 save

# Enable PM2 startup
pm2 startup
```

## Cloud Deployment

### Heroku

#### Backend
```bash
cd backend
heroku create grib-viewer-backend
heroku buildpacks:add --index 1 heroku-community/apt
echo "libeccodes-dev" > Aptfile
git add Aptfile
git commit -m "Add ecCodes dependency"
git push heroku main
```

#### Frontend
```bash
cd frontend
heroku create grib-viewer-frontend
git push heroku main
```

### AWS

#### EC2 Deployment
1. Launch an EC2 instance (Ubuntu recommended)
2. Install Docker and Docker Compose
3. Clone repository and run `docker-compose up -d`
4. Configure security groups to allow ports 80, 443, 3000, 8000

#### ECS/Fargate
1. Build and push Docker images to ECR
2. Create ECS task definitions for backend and frontend
3. Deploy services using Fargate
4. Configure Application Load Balancer

### Google Cloud Platform

#### Cloud Run
1. Build and push images to Google Container Registry
2. Deploy backend:
```bash
gcloud run deploy grib-backend \
  --image gcr.io/PROJECT_ID/grib-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. Deploy frontend:
```bash
gcloud run deploy grib-frontend \
  --image gcr.io/PROJECT_ID/grib-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### DigitalOcean

#### App Platform
1. Connect your repository
2. Configure two components:
   - Backend (Python, port 8000)
   - Frontend (Node.js, port 3000)
3. Set environment variables
4. Deploy

## Configuration

### Backend Environment Variables

```bash
HOST=0.0.0.0                    # Server host
PORT=8000                        # Server port
GRIB_STORAGE_PATH=./grib_files  # Path for storing GRIB files
ALLOWED_ORIGINS=http://localhost:3000  # CORS allowed origins (comma-separated)
```

### Frontend Environment Variables

```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000  # Backend API URL
```

## Nginx Reverse Proxy

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name example.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## SSL/TLS

Use Let's Encrypt with Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com
```

## Monitoring

Consider adding:
- Application monitoring (New Relic, DataDog)
- Error tracking (Sentry)
- Logging (ELK stack, CloudWatch)
- Uptime monitoring (UptimeRobot, Pingdom)

## Security Considerations

1. Use HTTPS in production
2. Set strong CORS policies
3. Implement rate limiting
4. Add authentication/authorization if needed
5. Keep dependencies updated
6. Regular security audits
7. Backup GRIB files regularly

## Performance Optimization

1. Use a CDN for frontend assets
2. Enable gzip compression
3. Cache GRIB data responses
4. Use a reverse proxy (Nginx)
5. Scale horizontally with load balancer
6. Consider Redis for caching

## Troubleshooting

### Backend issues
- Check ecCodes installation: `grib_ls --version`
- Verify Python dependencies: `pip list`
- Check logs: `docker logs <container_id>`

### Frontend issues
- Clear node_modules and reinstall
- Check environment variables
- Verify API connectivity
- Check browser console for errors

## Support

For issues and questions, please open an issue on GitHub.
