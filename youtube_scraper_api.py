from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from googleapiclient.discovery import build
import pandas as pd
import os
import tempfile
from typing import Optional
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="YouTube Video Scraper API", version="1.0.0")

# Get API key from environment variable
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")

class VideoData(BaseModel):
    video_title: str
    channel_name: str
    video_link: str
    upload_date: str
    views: str
    channel_subscribers: str

class SearchResponse(BaseModel):
    query: str
    total_results: int
    videos: list[VideoData]

def get_video_data_with_views(api_key: str, query: str, max_total_results: int = 200):
    """
    Searches YouTube for videos and collects a specified number of results using pagination.
    It then gets the view counts for all collected videos and channel subscriber counts.
    """
    try:
        # Build the YouTube service object
        youtube = build("youtube", "v3", developerKey=api_key)

        video_data = []
        next_page_token = None

        # Step 1: Paginate to collect video IDs and basic info
        while len(video_data) < max_total_results:
            search_request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=min(50, max_total_results - len(video_data)),
                pageToken=next_page_token
            )
            search_response = search_request.execute()

            for item in search_response.get("items", []):
                # Correcting the video link to use the video ID
                video_data.append({
                    "Video ID": item["id"]["videoId"],
                    "Video Title": item["snippet"]["title"],
                    "Channel Name": item["snippet"]["channelTitle"],
                    "Channel ID": item["snippet"]["channelId"],
                    # This line has been corrected to form a valid video URL
                    "Video Link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "Upload Date": item["snippet"]["publishedAt"]
                })

            next_page_token = search_response.get("nextPageToken")

            # Break the loop if there are no more pages
            if not next_page_token:
                break

        # Step 2: Get detailed statistics (including view counts) for all collected videos
        video_ids = [video["Video ID"] for video in video_data]

        # Process video IDs in chunks of 50, as the videos.list endpoint has a 50-item limit
        for i in range(0, len(video_ids), 50):
            chunk_ids = video_ids[i:i + 50]

            videos_request = youtube.videos().list(
                part="statistics",
                id=",".join(chunk_ids)
            )
            videos_response = videos_request.execute()

            # Map view counts to the video data
            stats_map = {item["id"]: item["statistics"].get("viewCount", "N/A") for item in videos_response.get("items", [])}

            for video in video_data:
                if video["Video ID"] in stats_map:
                    video["Views"] = stats_map[video["Video ID"]]

        # Step 3: Get channel subscriber counts
        # Get unique channel IDs
        channel_ids = list(set([video["Channel ID"] for video in video_data]))
        
        # Process channel IDs in chunks of 50
        for i in range(0, len(channel_ids), 50):
            chunk_channel_ids = channel_ids[i:i + 50]
            
            channels_request = youtube.channels().list(
                part="statistics",
                id=",".join(chunk_channel_ids)
            )
            channels_response = channels_request.execute()
            
            # Map subscriber counts to channel data
            subscriber_map = {}
            for item in channels_response.get("items", []):
                subscriber_count = item["statistics"].get("subscriberCount", "N/A")
                subscriber_map[item["id"]] = subscriber_count
            
            # Add subscriber count to video data
            for video in video_data:
                if video["Channel ID"] in subscriber_map:
                    video["Channel Subscribers"] = subscriber_map[video["Channel ID"]]

        # Remove the temporary columns before exporting
        for video in video_data:
            del video["Video ID"]
            del video["Channel ID"]

        return video_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.get("/")
async def root():
    return {"message": "YouTube Video Scraper API", "version": "1.0.0"}

@app.get("/search", response_model=SearchResponse)
async def search_videos(
    query: str = Query(..., description="Search query for YouTube videos"),
    max_results: int = Query(100, ge=1, le=500, description="Maximum number of results to return (1-500)")
):
    """
    Search for YouTube videos and return the data as JSON.
    """
    try:
        video_data = get_video_data_with_views(API_KEY, query, max_results)
        
        if video_data is None:
            raise HTTPException(status_code=500, detail="Failed to fetch video data")
        
        # Convert to Pydantic models
        videos = []
        for video in video_data:
            videos.append(VideoData(
                video_title=video["Video Title"],
                channel_name=video["Channel Name"],
                video_link=video["Video Link"],
                upload_date=video["Upload Date"],
                views=video["Views"],
                channel_subscribers=video.get("Channel Subscribers", "N/A")
            ))
        
        return SearchResponse(
            query=query,
            total_results=len(videos),
            videos=videos
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching videos: {str(e)}")

@app.get("/download")
async def download_videos_excel(
    query: str = Query(..., description="Search query for YouTube videos"),
    max_results: int = Query(100, ge=1, le=500, description="Maximum number of results to return (1-500)"),
    filename: Optional[str] = Query(None, description="Custom filename for the Excel file")
):
    """
    Search for YouTube videos and download the data as an Excel file.
    """
    try:
        video_data = get_video_data_with_views(API_KEY, query, max_results)
        
        if video_data is None:
            raise HTTPException(status_code=500, detail="Failed to fetch video data")
        
        # Create DataFrame
        df = pd.DataFrame(video_data)
        
        # Generate filename if not provided
        if not filename:
            # Clean query for filename
            clean_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_query = clean_query.replace(' ', '_')
            filename = f"youtube_videos_{clean_query}_{len(video_data)}_results.xlsx"
        
        # Ensure filename has .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            
            return FileResponse(
                path=tmp_file.name,
                filename=filename,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Excel file: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
