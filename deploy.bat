@echo off
echo 🚀 Starting YouTube Scraper API deployment...

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo 📝 Please create .env file from config.env.example:
    echo    copy config.env.example .env
    echo    Then edit .env and add your YOUTUBE_API_KEY
    pause
    exit /b 1
)

REM Check if YOUTUBE_API_KEY is set
findstr /C:"YOUTUBE_API_KEY=your_youtube_api_key_here" .env >nul
if %errorlevel% equ 0 (
    echo ❌ YOUTUBE_API_KEY not set in .env file!
    echo 📝 Please edit .env file and add your YouTube API key
    pause
    exit /b 1
)

REM Create logs directory
if not exist logs mkdir logs

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose down 2>nul

REM Build and start the application
echo 🔨 Building and starting the application...
docker-compose up --build -d

REM Wait for the application to start
echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if the application is running
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Application is running successfully!
    echo 🌐 API is available at: http://localhost:8000
    echo 📚 API documentation: http://localhost:8000/docs
    echo 📊 Health check: http://localhost:8000/health
    echo.
    echo 📋 Useful commands:
    echo    View logs: docker-compose logs -f
    echo    Stop app: docker-compose down
    echo    Restart: docker-compose restart
) else (
    echo ❌ Application failed to start!
    echo 📋 Check logs with: docker-compose logs
    pause
    exit /b 1
)

pause
