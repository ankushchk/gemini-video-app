import json
import re
import shutil
import uvicorn
import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
from video_analyzer import analyze_video_file
from transcript_parser import parse_transcript
from podcast_analyzer import analyze_podcast
from video_renderer import render_video_clip
from fastapi.responses import FileResponse
import json

from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount uploads directory to serve generated thumbnails
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# IMPORTANT: This allows your React app (on port 5173) to talk to Python (on port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    transcript: Optional[UploadFile] = File(None),
    start_time: Optional[float] = Form(None),
    end_time: Optional[float] = Form(None),
    topic: Optional[str] = Form(None),
    caption_style: Optional[str] = Form(None)
):
    """
    Multimodal Video Analysis Endpoint
    Uses Gemini 2.5 Flash to watch and analyze video directly.
    """
    # Save the file locally - use a fixed name or manage sessions in production
    # For Hackathon, we'll keep the original filename to reference it later for cutting
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    print(f"Receiving video upload: {file.filename}")
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        transcript_location = None
        if transcript:
            print(f"Receiving transcript upload: {transcript.filename}")
            transcript_location = f"uploads/{transcript.filename}"
            with open(transcript_location, "wb") as buffer:
                shutil.copyfileobj(transcript.file, buffer)
        
        # Analyze video using new module
        result = analyze_video_file(
            file_location, 
            transcript_path=transcript_location,
            start_time=start_time,
            end_time=end_time,
            topic=topic,
            caption_style=caption_style
        )
        
        # Add the 'source_file' path to the result so the frontend knows what to cut later
        # We return the RELATIVE path that the backend can understand
        result["source_file"] = file_location
            
        return result
        
    except Exception as e:
        print(f"Error in upload_video: {e}")
        return {"error": str(e)}

@app.post("/export-clip")
async def export_clip(
    source_file: str = Form(...),
    clip_data: str = Form(...) # JSON string of the clip object
):
    """
    Renders a clip with burned-in captions using FFmpeg.
    """
    try:
        # Create 'exports' directory
        os.makedirs("exports", exist_ok=True)
        
        # Parse clip data
        clip = json.loads(clip_data)
        clip_id = clip.get('clip_id', 'clip_unknown')
        
        output_filename = f"{clip_id}_rendered.mp4"
        output_path = os.path.join("exports", output_filename)
        
        # Check if source exists or is a URL
        if source_file.startswith("http"):
            print(f"Source is a URL, downloading video: {source_file}")
            from youtube_helper import download_youtube_video
            downloaded_path = download_youtube_video(source_file)
            if not downloaded_path:
                return {"error": "Failed to download YouTube video for export."}
            source_file = downloaded_path
            print(f"Video downloaded to: {source_file}")
            
        if not os.path.exists(source_file):
            return {"error": f"Source file not found: {source_file}"}
            
        print(f"Requesting render for {clip_id}...")
            
        # Call the appropriate renderer (advanced)
        # We ignore start_time/end_time form fields as they are in the JSON now
        rendered_path = render_video_clip(source_file, clip, output_path)
        
        # Return the file
        return FileResponse(rendered_path, media_type="video/mp4", filename=output_filename)
        
    except Exception as e:
        print(f"Error exporting clip: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}



@app.post("/render-vertical")
async def render_vertical_endpoint(
    source_file: str = Form(...),
    clip_data: str = Form(...) 
):
    """
    Renders a vertical 9:16 video clip (blur-fill) for Reels/TikTok.
    Does NOT burn text (handled by frontend).
    """
    try:
        # Create 'exports' directory
        os.makedirs("exports", exist_ok=True)
        
        # Parse clip data
        clip = json.loads(clip_data)
        clip_id = clip.get('clip_id', 'clip_unknown')
        
        output_filename = f"{clip_id}_vertical.mp4"
        output_path = os.path.join("exports", output_filename)
        
        # Check if source exists or is a URL
        if source_file.startswith("http"):
            # Reuse download logic (should be cached if hash matches, but for now simple check)
            # The download_youtube_video function uses ID-based filenames so it acts as cache
            from youtube_helper import download_youtube_video
            downloaded_path = download_youtube_video(source_file)
            if not downloaded_path:
                return {"error": "Failed to download YouTube video."}
            source_file = downloaded_path
            
        if not os.path.exists(source_file):
            return {"error": f"Source file not found: {source_file}"}
            
        print(f"Requesting VERTICAL render for {clip_id}...")
        
        # Import dynamically to avoid circular imports if any
        from video_renderer import render_vertical_video
        
        rendered_path = render_vertical_video(source_file, clip, output_path)
        
        # Return the file
        return FileResponse(rendered_path, media_type="video/mp4", filename=output_filename)
        
    except Exception as e:
        print(f"Error rendering vertical clip: {e}")
        return {"error": str(e)}

@app.post("/analyze-podcast")
async def analyze_podcast_endpoint(
    file: UploadFile = File(...),
    guest: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    tone: Optional[str] = Form(None)
):
    """
    New endpoint for podcast transcript analysis
    Accepts: .txt, .srt, .vtt transcript files
    Optional metadata: guest, topic, tone
    """
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Determine file format from extension
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['txt', 'srt', 'vtt']:
            return {"error": f"Unsupported file format: {file_ext}. Use .txt, .srt, or .vtt"}
        
        # Parse transcript
        print(f"Parsing {file_ext} transcript...")
        transcript_entries = parse_transcript(content_str, file_ext)
        
        if not transcript_entries:
            return {"error": "No transcript entries found. Check file format."}
        
        print(f"Parsed {len(transcript_entries)} transcript entries")
        
        # Build metadata
        metadata = {}
        if guest:
            metadata['guest'] = guest
        if topic:
            metadata['topic'] = topic
        if tone:
            metadata['tone'] = tone
        
        # Analyze podcast
        result = analyze_podcast(transcript_entries, metadata if metadata else None)
        
        return result
        
    except Exception as e:
        print(f"Error in analyze_podcast_endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}



from youtube_helper import get_youtube_transcript, get_video_title

class YouTubeRequest(BaseModel):
    video_url: str
    guest: Optional[str] = None
    topic: Optional[str] = None
    tone: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    caption_style: Optional[str] = None

@app.post("/get-video-meta")
async def get_video_meta_endpoint(request: YouTubeRequest):
    """
    Fast endpoint to get video metadata (title, duration, thumb) for the dashboard.
    """
    from youtube_helper import get_video_metadata
    meta = get_video_metadata(request.video_url)
    if not meta:
        return {"error": "Failed to fetch metadata"}
    return meta

@app.post("/analyze-youtube")
async def analyze_youtube_endpoint(request: YouTubeRequest):
    """
    Analyzes a YouTube video by fetching its transcript.
    """
    try:
        print(f"Fetching transcript for: {request.video_url}")
        transcript = get_youtube_transcript(request.video_url)
        
        # Filter transcript by start/end time if provided
        if request.start_time is not None or request.end_time is not None:
            start = request.start_time or 0
            end = request.end_time or float('inf')
            print(f"Trimming transcript to {start}-{end}s")
            transcript = [
                t for t in transcript 
                if t['start'] + t['duration'] >= start and t['start'] <= end
            ]
        # yt-api: [{'text': '...', 'start': 0.0, 'duration': 1.0}, ...]
        # our format: same structure is fine as long as keys match
        
        transcript_entries = [
            {
                "text": entry["text"],
                "start_time": entry["start"],
                "end_time": entry["start"] + entry["duration"],
                "speaker": "Speaker" # Default speaker since YouTube doesn't provide speaker diarization
            }
            for entry in transcript
        ]
        
        print(f"Fetched {len(transcript_entries)} transcript entries")
        
        # Build metadata
        metadata = {}
        if request.guest:
            metadata['guest'] = request.guest
        if request.topic:
            metadata['topic'] = request.topic
        if request.tone:
            metadata['tone'] = request.tone
            
        metadata['source_url'] = request.video_url
        
        # Try to get video title
        video_title = get_video_title(request.video_url)
        if video_title:
            print(f"Found video title: {video_title}")
            metadata['title'] = video_title
        
        # Analyze podcast
        result = analyze_podcast(transcript_entries, metadata if metadata else None)
        
        return result

    except Exception as e:
        print(f"Error in analyze_youtube: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)