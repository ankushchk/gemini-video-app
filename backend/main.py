import json
import re
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from scout_agent import analyze_video
from transcript_parser import parse_transcript
from podcast_analyzer import analyze_podcast

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
    """Legacy endpoint for video analysis"""
    # Save the file locally so the Gemini Agent can 'Scout' it later
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze video
    try:
        analysis_result = analyze_video(file_location)
        
        # Extract JSON from code blocks if present
        json_match = re.search(r'```json\n(.*?)\n```', analysis_result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = analysis_result
            
        data = json.loads(json_str)
        return data
    except Exception as e:
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)