"""
Video Analyzer - Multimodal Analysis Pipeline
Uses Gemini 2.5 Flash to watch/listen to video files directly
"""
import os
import time
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Setup Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = client.files.upload(file=path)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = client.files.get(name=name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            file = client.files.get(name=name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")

def create_video_analysis_prompt() -> str:
    """
    Create comprehensive prompt for video analysis.
    Output schema MUST match the one in podcast_analyzer.py for frontend compatibility.
    """
    return """You are a viral content strategist and video editor.
    
    YOUR TASK:
    Watch/Listen to this video. Identify the top 3-5 most viral moments (30-60 seconds each).
    Return a comprehensive JSON analysis.

    For each clip, you must provide:
    1. Timestamps (exact start/end seconds).
    2. Viral Score (0.0-1.0) and Reasoning.
    3. Platform Optimization (Hooks, Captions, Hashtags).
    4. Visual Treatment (Describe what we are seeing or what b-roll to add).

    OUTPUT FORMAT:
    Return ONLY valid JSON in this exact structure:

    ```json
    {
      "chunks": [
        {
          "chunk_id": "chunk_01",
          "start_time": 0.0,
          "end_time": 60.0,
          "duration": 60.0,
          "speakers": ["Speaker A"],
          "summary": "Brief summary of this segment"
        }
      ],
      "analysis": [
        {
          "chunk_id": "chunk_01",
          "viral_score": 0.9,
          "editorial_reasoning": "Strong emotional hook...",
          "context_dependency": false,
          "platform_fit": "Perfect for TikTok"
        }
      ],
      "selected_clips": [
        {
          "clip_id": "clip_01",
          "chunk_id": "chunk_01",
          "start": 0.0,
          "end": 60.0,
          "refined_start": 2.0,
          "refined_end": 58.0,
          "refined_duration": 56.0,
          "viral_score": 0.9,
          "reasoning": "High energy...",
          "hook": "You won't believe this...",
          "captions": [
            {
              "text": "First phrase",
              "start_offset": 0.0,
              "end_offset": 2.0,
              "emphasis": ["First"]
            }
          ],
          "reel_caption": "Caption for the post...",
          "hashtags": ["#viral"],
          "visual_beats": [
            {
              "image_concept": "Description of visual",
              "text_overlay": "Overlay text",
              "motion": "zoom-in",
              "motion_intensity": 5,
              "duration": 5
            }
          ],
          "assembly_spec": {
            "aspect_ratio": "9:16",
            "resolution": "1080x1920"
          }
        }
      ]
    }
    ```
    """

def analyze_video_file(video_path: str) -> dict:
    """
    Main function to analyze a video file.
    
    Args:
        video_path: Local path to the video file
    """
    print(f"Starting video analysis for: {video_path}")
    
    try:
        # 1. Upload Video
        video_file = upload_to_gemini(video_path, mime_type="video/mp4")
        
        # 2. Wait for processing
        wait_for_files_active([video_file])
        
        # 3. Generate Content
        prompt = create_video_analysis_prompt()
        print("Requesting Gemini 2.5 Flash analysis...")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # 4. Parse Response
        result_text = response.text
        try:
            result = json.loads(result_text)
            print(f"Analysis complete! Found {len(result.get('selected_clips', []))} clips.")
            return result
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"error": "Failed to parse JSON response", "raw_response": result_text}
            
    except Exception as e:
        print(f"Video analysis failed: {e}")
        return {"error": str(e)}
