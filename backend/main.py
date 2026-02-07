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

app = FastAPI()

# IMPORTANT: This allows your React app (on port 5173) to talk to Python (on port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
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
        
        # Analyze video using new module
        result = analyze_video_file(file_location)
        
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
        
        # Check if source exists
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



from youtube_helper import get_youtube_transcript

class YouTubeRequest(BaseModel):
    video_url: str
    guest: Optional[str] = None
    topic: Optional[str] = None
    tone: Optional[str] = None

@app.post("/analyze-youtube")
async def analyze_youtube_endpoint(request: YouTubeRequest):
    """
    Analyzes a YouTube video by fetching its transcript.
    """
    try:
        print(f"Fetching transcript for: {request.video_url}")
        transcript = get_youtube_transcript(request.video_url)
        
        # Convert transcript format from youtube-api to our format
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
        
        # Analyze podcast
        result = analyze_podcast(transcript_entries, metadata if metadata else None)
        
        return result

    except Exception as e:
        print(f"Error in analyze_youtube: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)