# YouTube Video Scraper API

A FastAPI application that scrapes YouTube video data and provides endpoints to get video information and download data as Excel files.

## Features

- Search YouTube videos by query
- Get video data including title, channel, link, upload date, view count, and channel subscriber count
- Download results as Excel files
- Configurable number of results (1-500)
- RESTful API with automatic documentation
- Docker support for easy deployment

## Installation

### Option 1: Docker Deployment (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd youtube-video-scraping
```

2. Get a YouTube Data API key from [Google Cloud Console](https://console.cloud.google.com/)

3. Create environment file:
```bash
cp config.env.example .env
```

4. Edit `.env` file and add your YouTube API key:
```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
```

5. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

### Option 2: Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a YouTube Data API key from [Google Cloud Console](https://console.cloud.google.com/)

3. Set environment variable:
```bash
export YOUTUBE_API_KEY=your_youtube_api_key_here
```

4. Start the server:
```bash
python youtube_scraper_api.py
```

The API will be available at http://localhost:8000

## Docker Commands

### Build and run:
```bash
docker-compose up --build
```

### Run in background:
```bash
docker-compose up -d
```

### Stop the service:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f
```

### Rebuild without cache:
```bash
docker-compose build --no-cache
```

## API Endpoints

#### 1. Get Video Data (JSON)
- **URL**: /search
- **Method**: GET
- **Parameters**:
  - query (required): Search query for YouTube videos
  - max_results (optional): Maximum number of results (1-500, default: 100)

**Example**:
```
GET http://localhost:8000/search?query=Korean skincare product review&max_results=50
```

#### 2. Download Video Data (Excel)
- **URL**: /download
- **Method**: GET
- **Parameters**:
  - query (required): Search query for YouTube videos
  - max_results (optional): Maximum number of results (1-500, default: 100)
  - filename (optional): Custom filename for the Excel file

**Example**:
```
GET http://localhost:8000/download?query=Korean skincare product review&max_results=200&filename=my_videos.xlsx
```

#### 3. Health Check
- **URL**: /health
- **Method**: GET

#### 4. API Documentation
- **URL**: /docs (Swagger UI)
- **URL**: /redoc (ReDoc)

## Response Format

### JSON Response (from /search):
```json
{
  "query": "Korean skincare product review",
  "total_results": 50,
  "videos": [
    {
      "video_title": "Best Korean Skincare Products 2024",
      "channel_name": "Beauty Channel",
      "video_link": "https://www.youtube.com/watch?v=VIDEO_ID",
      "upload_date": "2024-01-15T10:30:00Z",
      "views": "125000",
      "channel_subscribers": "500000"
    }
  ]
}
```

### Excel File (from /download):
The Excel file contains columns:
- Video Title
- Channel Name
- Video Link
- Upload Date
- Views
- Channel Subscribers

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Yes |
| `APP_HOST` | Application host (default: 0.0.0.0) | No |
| `APP_PORT` | Application port (default: 8000) | No |
| `APP_DEBUG` | Debug mode (default: false) | No |
| `LOG_LEVEL` | Logging level (default: INFO) | No |

## Notes

- The API uses YouTube Data API v3
- Rate limits apply based on your YouTube API quota
- Maximum 500 results per request
- Excel files are generated with temporary files and cleaned up automatically
- Channel subscriber counts are fetched for each unique channel in the results
- For production deployment, make sure to secure your API key and use HTTPS

## Development

### Running Tests
```bash
python test_api.py
```

### Building Docker Image
```bash
docker build -t youtube-scraper-api .
```

### Running Docker Container
```bash
docker run -p 8000:8000 -e YOUTUBE_API_KEY=your_key_here youtube-scraper-api
```