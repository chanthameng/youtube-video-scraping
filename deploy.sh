#!/bin/bash

# YouTube Scraper API Deployment Script

set -e

echo "🚀 Starting YouTube Scraper API deployment..."

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
docker-compose down 2>/dev/null || true

# Build and start the application
echo "🔨 Building and starting the application..."
docker-compose up --build -d

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 API is available at: http://localhost:8000"
    echo "📚 API documentation: http://localhost:8000/docs"
    echo "📊 Health check: http://localhost:8000/health"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop app: docker-compose down"
    echo "   Restart: docker-compose restart"
else
    echo "❌ Application failed to start!"
    echo "📋 Check logs with: docker-compose logs"
    exit 1
fi
