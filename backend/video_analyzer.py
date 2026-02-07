"""
Video Analyzer - Multimodal Analysis Pipeline
Uses Gemini 3 Flash Preview (latest) with native Structured Outputs for reliability
"""
import os
import time
import json
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Setup Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Pydantic Models for Structured Output ---

# STAGE 1 MODELS
class CandidateClip(BaseModel):
    id: str
    start_time: float
    end_time: float
    description: str

class ScoutResult(BaseModel):
    candidates: List[CandidateClip]

# STAGE 2 MODELS
class VideoChunk(BaseModel):
    chunk_id: str
    start_time: float
    end_time: float
    duration: float
    speakers: List[str]
    summary: str

class ChunkAnalysis(BaseModel):
    chunk_id: str
    viral_score: float
    editorial_reasoning: str
    context_dependency: bool
    platform_fit: str

class VisualBeat(BaseModel):
    image_concept: str
    text_overlay: Optional[str] = None
    motion: str
    motion_intensity: int
    duration: int

class AssemblySpec(BaseModel):
    aspect_ratio: str = "9:16"
    resolution: str = "1080x1920"

class Caption(BaseModel):
    text: str
    start_offset: float
    end_offset: float
    emphasis: List[str]

class SelectedClip(BaseModel):
    clip_id: str
    chunk_id: str
    start: float
    end: float
    refined_start: float
    refined_end: float
    refined_duration: float
    viral_score: float
    reasoning: str
    hook: str
    captions: List[Caption]
    reel_caption: str
    hashtags: List[str]
    visual_beats: List[VisualBeat]
    assembly_spec: AssemblySpec

class VideoAnalysisResult(BaseModel):
    chunks: List[VideoChunk]
    analysis: List[ChunkAnalysis]
    selected_clips: List[SelectedClip]


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

def create_draft_prompt() -> str:
    """
    Stage 1: The Scout Agent
    Focus: finding potential candidates with rough timestamps.
    """
    return """You are a podcast scout.
    
    YOUR TASK:
    Watch/Listen to this video. Identify 5 potential viral moments (30-60 seconds each).
    Don't worry about perfect timing yet. Just find the best content hooks.
    
    Return a list of candidate clips.
    """

def create_verification_prompt(draft_clips_json: str) -> str:
    """
    Stage 2: The Senior Editor Agent
    Focus: Precision timing and final output formatting.
    """
    return f"""You are a senior video editor.
    
    YOUR TASK:
    Review these candidate clips from the scout:
    {draft_clips_json}

    1. VERIFY: Watch strictly within the proposed timestamps.
    2. REFINE: 
       - Adjust start/end times to valid sentence boundaries (don't cut words).
       - Ensure duration is between 25-60 seconds.
       - Discard any clips that are actually boring or low quality.
    3. FINALIZE: Generate the full production schema.

    Return the final analysis including selected clips details.
    """

def analyze_video_file(video_path: str) -> dict:
    """
    Main function to analyze a video file using 2-Stage Agentic Loop.
    
    Args:
        video_path: Local path to the video file
    """
    print(f"Starting AGENTIC video analysis for: {video_path}")
    
    try:
        # 1. Upload Video
        video_file = upload_to_gemini(video_path, mime_type="video/mp4")
        
        # 2. Wait for processing
        wait_for_files_active([video_file])
        
        # --- STAGE 1: DRAFTING (The Scout) ---
        print("🎬 Stage 1: The Scout (Drafting Candidates)...")
        draft_prompt = create_draft_prompt()
        
        draft_response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[video_file, draft_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ScoutResult
            )
        )
        
        # Parse result into Pydantic model
        scout_result = ScoutResult(**json.loads(draft_response.text))
        candidates = scout_result.candidates
        print(f"Found {len(candidates)} candidate clips.")
        
        # --- STAGE 2: VERIFICATION (The Senior Editor) ---
        print("🕵️ Stage 2: Senior Editor (Verifying & Refining)...")
        # Dump candidates to JSON for the next prompt
        verify_prompt = create_verification_prompt(scout_result.model_dump_json())
        
        final_response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[video_file, verify_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VideoAnalysisResult
            )
        )
        
        # 4. Parse Final Response
        final_result_model = VideoAnalysisResult(**json.loads(final_response.text))
        final_dict = final_result_model.model_dump()
        
        final_count = len(final_dict.get('selected_clips', []))
        print(f"Analysis complete! Final Approved Clips: {final_count}")
        return final_dict
            
    except Exception as e:
        print(f"Video analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
