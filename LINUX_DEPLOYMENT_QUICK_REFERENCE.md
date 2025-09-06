# Linux Server Deployment - Quick Reference

## 🚀 Quick Start Commands

### 1. Basic Deployment
```bash
# Clone repository
git clone <your-repo-url>
cd youtube-video-scraping

# Set up environment
cp config.env.example .env
nano .env  # Add your YouTube API key

# Deploy
docker-compose -f docker-compose.prod.yml up --build -d
```

### 2. Using the Deployment Script
```bash
# Make script executable
chmod +x deploy-linux.sh

# Run deployment
./deploy-linux.sh
```

## 📋 Essential Commands

### Start/Stop/Restart
```bash
# Start (production)
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# Restart
docker-compose -f docker-compose.prod.yml restart
```

### Monitoring
```bash
# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Health check
curl http://localhost:8000/health
```

### Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Standard deployment |
| `docker-compose.prod.yml` | Production (recommended) |
| `docker-compose.dev.yml` | Development with hot reload |
| `.env` | Environment variables |

## 🌐 Access URLs

- **API**: http://your-server-ip:8000
- **Docs**: http://your-server-ip:8000/docs
- **Health**: http://your-server-ip:8000/health

## 🔥 Firewall Setup
```bash
# Allow port 8000
sudo ufw allow 8000

# Check status
sudo ufw status
```

## 📊 Production Features

The `docker-compose.prod.yml` includes:
- ✅ Resource limits (512MB memory)
- ✅ Restart policy (always)
- ✅ Health checks
- ✅ Optimized logging
- ✅ Security best practices

## 🆘 Troubleshooting

### Container won't start
```bash
docker-compose -f docker-compose.prod.yml logs
```

### Port conflict
```bash
sudo netstat -tulpn | grep :8000
```

### Permission issues
```bash
sudo chown -R $USER:$USER logs/
```

## 🔄 Automated Deployment

Create a cron job for automatic updates:
```bash
# Edit crontab
crontab -e

# Add this line for daily updates at 2 AM
0 2 * * * cd /path/to/youtube-video-scraping && git pull && docker-compose -f docker-compose.prod.yml up --build -d
```
