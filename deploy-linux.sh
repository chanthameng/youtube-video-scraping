#!/bin/bash

# YouTube Scraper API Linux Deployment Script

set -e

echo "🚀 Starting YouTube Scraper API deployment on Linux..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "📝 Please install Docker first:"
    echo "   sudo apt update && sudo apt install docker.io docker-compose-plugin"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
    echo "❌ Docker Compose is not available!"
    echo "📝 Please install Docker Compose first"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please create .env file from config.env.example:"
    echo "   cp config.env.example .env"
    echo "   Then edit .env and add your YOUTUBE_API_KEY"
    exit 1
fi

# Check if YOUTUBE_API_KEY is set
if ! grep -q "YOUTUBE_API_KEY=" .env || grep -q "YOUTUBE_API_KEY=your_youtube_api_key_here" .env; then
    echo "❌ YOUTUBE_API_KEY not set in .env file!"
    echo "📝 Please edit .env file and add your YouTube API key"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Stop existing containers
echo "🛑 Stopping existing containers..."
if docker compose version &> /dev/null; then
    docker compose -f docker-compose.prod.yml down 2>/dev/null || true
else
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
fi

# Build and start the application
echo "🔨 Building and starting the application..."
if docker compose version &> /dev/null; then
    docker compose -f docker-compose.prod.yml up --build -d
else
    docker-compose -f docker-compose.prod.yml up --build -d
fi

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 15

# Check if the application is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 API is available at: http://localhost:8000"
    echo "📚 API documentation: http://localhost:8000/docs"
    echo "📊 Health check: http://localhost:8000/health"
    echo ""
    echo "📋 Useful commands:"
    if docker compose version &> /dev/null; then
        echo "   View logs: docker compose -f docker-compose.prod.yml logs -f"
        echo "   Stop app: docker compose -f docker-compose.prod.yml down"
        echo "   Restart: docker compose -f docker-compose.prod.yml restart"
    else
        echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
        echo "   Stop app: docker-compose -f docker-compose.prod.yml down"
        echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
    fi
    echo ""
    echo "🔧 For external access, make sure to:"
    echo "   1. Open port 8000 in firewall: sudo ufw allow 8000"
    echo "   2. Replace localhost with your server IP in URLs above"
else
    echo "❌ Application failed to start!"
    echo "📋 Check logs with:"
    if docker compose version &> /dev/null; then
        echo "   docker compose -f docker-compose.prod.yml logs"
    else
        echo "   docker-compose -f docker-compose.prod.yml logs"
    fi
    exit 1
fi
