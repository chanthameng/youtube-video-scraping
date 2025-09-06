# Linux Server Deployment Guide

## Prerequisites

1. **Docker & Docker Compose installed on Linux server**
2. **Git** (to clone the repository)
3. **YouTube API Key**

## Installation Steps

### 1. Install Docker & Docker Compose (if not already installed)

```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd youtube-video-scraping
```

### 3. Set Up Environment Variables

```bash
# Copy the environment template
cp config.env.example .env

# Edit the .env file with your API key
nano .env
# or
vim .env
```

Edit the `.env` file:
```bash
YOUTUBE_API_KEY=your_actual_youtube_api_key_here
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
LOG_LEVEL=INFO
```

## Deployment Options

### Option 1: Development Deployment
```bash
# Build and run in development mode
docker-compose -f docker-compose.dev.yml up --build -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Option 2: Production Deployment (Recommended)
```bash
# Build and run in production mode
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 3: Standard Deployment
```bash
# Build and run with default configuration
docker-compose up --build -d

# View logs
docker-compose logs -f
```

## Production Server Commands

### Start the Service
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Or standard deployment
docker-compose up -d
```

### Stop the Service
```bash
# Production
docker-compose -f docker-compose.prod.yml down

# Standard
docker-compose down
```

### Restart the Service
```bash
# Production
docker-compose -f docker-compose.prod.yml restart

# Standard
docker-compose restart
```

### Update the Service
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d
```

### View Service Status
```bash
# Check running containers
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check resource usage
docker stats
```

## Firewall Configuration

If you need to expose the API to external access:

```bash
# Allow port 8000 through firewall
sudo ufw allow 8000

# Check firewall status
sudo ufw status
```

## Nginx Reverse Proxy (Optional)

For production, consider using Nginx as a reverse proxy:

```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/youtube-scraper
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/youtube-scraper /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## SSL Certificate (Optional)

For HTTPS with Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Maintenance

### Health Check
```bash
# Check if API is responding
curl http://localhost:8000/health

# Or from external
curl http://your-server-ip:8000/health
```

### Log Management
```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f

# View system logs
sudo journalctl -u docker.service -f
```

### Backup
```bash
# Backup logs directory
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Backup environment file
cp .env .env.backup
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check container status
docker ps -a

# Remove and rebuild
docker-compose down
docker-compose up --build
```

### Port already in use
```bash
# Check what's using port 8000
sudo netstat -tulpn | grep :8000

# Kill process if needed
sudo kill -9 <PID>
```

### Permission issues
```bash
# Fix log directory permissions
sudo chown -R $USER:$USER logs/

# Fix Docker permissions
sudo chmod 666 /var/run/docker.sock
```

## Quick Deployment Script

Create a deployment script for easy updates:

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Deploying YouTube Scraper API..."

# Pull latest code
git pull

# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Build and start
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for health check
sleep 10

# Check status
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "🌐 API available at: http://your-server-ip:8000"
else
    echo "❌ Deployment failed!"
    docker-compose -f docker-compose.prod.yml logs
fi
```

Make it executable:
```bash
chmod +x deploy.sh
./deploy.sh
```
