# Deployment Guide

This guide covers different deployment options for the GRIB Viewer application.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Coolify Deployment](#coolify-deployment)
3. [Manual Deployment](#manual-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration](#configuration)

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

## Coolify Deployment

Coolify is a self-hosted PaaS platform that automatically handles port assignment, SSL certificates, and reverse proxying.

### Prerequisites
- A Coolify instance running
- Git repository access
- DNS records configured in Cloudflare (for separate frontend/backend URLs)

### Option 1: Single Service (Root Dockerfile)

For a simple deployment where frontend and backend are served together:

1. **Connect your repository to Coolify:**
   - In Coolify, create a new application
   - Connect your Git repository
   - Select "Dockerfile" as the build method

2. **Configure the application:**
   - **Dockerfile Path:** Use the root `Dockerfile` (not the backend one)
   - **Port:** Coolify will automatically assign a port and set the `PORT` environment variable
   - The application is configured to use the `PORT` env var automatically

3. **Set Environment Variables (optional):**
   ```
   GRIB_STORAGE_PATH=/app/grib_files
   ALLOWED_ORIGINS=*
   ```

4. **Deploy and access:**
   - Coolify will automatically build, assign ports, set up SSL, and create a reverse proxy
   - Access the application at the URL Coolify provides
   - API documentation will be available at `/docs`

### Option 2: Docker Compose with Separate Frontend/Backend URLs (Recommended)

For production deployments with separate domains for frontend and backend:

#### Setup in Cloudflare

1. Create two DNS records:
   - `A` record for frontend: `grib-viewer.yourdomain.com` → Your Coolify server IP
   - `A` record for backend: `api-grib.yourdomain.com` → Your Coolify server IP
   - Or use `CNAME` records if using Cloudflare proxy

#### Setup in Coolify

1. **Create Docker Compose Application:**
   - In Coolify, create a new application
   - Connect your Git repository
   - Select "Docker Compose" as the build method
   - **Docker Compose File:** `docker-compose.yml`

2. **Create Backend Service:**
   - Coolify will detect the `backend` service from docker-compose.yml
   - Configure the domain: `api-grib.yourdomain.com`
   - Set up SSL certificate (Coolify can do this automatically)

3. **Create Frontend Service:**
   - Coolify will detect the `frontend` service from docker-compose.yml
   - Configure the domain: `grib-viewer.yourdomain.com`
   - Set up SSL certificate (Coolify can do this automatically)

4. **Set Environment Variables in Coolify:**

   For the **backend** service, set:
   ```
   FRONTEND_URL=https://grib-viewer.yourdomain.com
   GRIB_STORAGE_PATH=/app/grib_files
   ```

   For the **frontend** service, set:
   ```
   BACKEND_URL=https://api-grib.yourdomain.com
   ```

   **Important:** These environment variables must be set in Coolify's environment variables section. They will be:
   - Used at build time for the frontend (to configure the API base URL)
   - Used at runtime for the backend (to configure CORS)

5. **Deploy:**
   - Coolify will build both services
   - Assign ports automatically
   - Set up SSL certificates for both domains
   - Create reverse proxies

6. **Access your application:**
   - Frontend: `https://grib-viewer.yourdomain.com`
   - Backend API: `https://api-grib.yourdomain.com`
   - API Documentation: `https://api-grib.yourdomain.com/docs`

### Notes
- **Port mappings:** Removed from docker-compose.yml - Coolify handles this automatically
- **Environment variables:** `BACKEND_URL` and `FRONTEND_URL` must be set in Coolify (not in docker-compose.yml)
- **Build time vs Runtime:** `BACKEND_URL` is used at build time for frontend, `FRONTEND_URL` is used at runtime for backend CORS
- **Persistent storage:** Configure volume mounts in Coolify for `/app/grib_files` in the backend service
- **SSL:** Coolify can automatically provision SSL certificates via Let's Encrypt

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
