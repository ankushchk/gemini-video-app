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

def create_draft_prompt(transcript_text: str = None, topic: str = None, start_time: float = None, end_time: float = None) -> str:
    """
    Stage 1: The Scout Agent
    Focus: finding potential candidates with rough timestamps.
    """
    transcript_context = ""
    if transcript_text:
        transcript_context = f"\n\nHere is the transcript for reference:\n{transcript_text}\n\nUse this transcript to identify key topics and hooks."

    topic_constraint = ""
    if topic:
        topic_constraint = f"\n\nFOCUS TOPIC: {topic}\nOnly select clips related to this topic."
        
    time_constraint = ""
    if start_time is not None and end_time is not None:
         time_constraint = f"\n\nTIME CONSTRAINT: Only select clips between {start_time}s and {end_time}s."

    return f"""You are a podcast scout.
    
    YOUR TASK:
    Watch/Listen to this video. Identify 5 potential viral moments.
    CRITICAL: Each clip MUST be at least 30 seconds long.
    Do not pick short 1-5 second snippets. We need full context.
    Target duration: 30-60 seconds.
    
    {transcript_context}
    {topic_constraint}
    {time_constraint}
    
    Return a list of candidate clips.
    """

def create_verification_prompt(draft_clips_json: str, style: str = None) -> str:
    """
    Stage 2: The Senior Editor Agent
    Focus: Precision timing and final output formatting.
    """
    style_instruction = ""
    if style:
        style_instruction = f"\n\nCAPTION STYLE: {style}\nEnsure the visual style matches this preference."

    return f"""You are a senior video editor.
    
    YOUR TASK:
    Review these candidate clips from the scout:
    {draft_clips_json}
    
    {style_instruction}

    1. VERIFY: Watch strictly within the proposed timestamps.
    2. REFINE: 
       - Adjust start/end times to valid sentence boundaries (don't cut words).
       - EXTEND the clip if needed to meet the duration requirement.
       - CRITICAL: Duration MUST be between 20 and 60 seconds.
       - REJECT any clip shorter than 15 seconds.
       - Discard any clips that are actually boring or low quality.
    3. FINALIZE: Generate the full production schema.

    Return the final analysis including selected clips details.
    """

def analyze_video_file(
    video_path: str, 
    transcript_path: str = None,
    start_time: float = None,
    end_time: float = None,
    topic: str = None,
    caption_style: str = None
) -> dict:
    """
    Main function to analyze a video file using 2-Stage Agentic Loop.
    
    Args:
        video_path: Local path to the video file
        transcript_path: Optional local path to a transcript file
        start_time: Optional start time constraint
        end_time: Optional end time constraint
        topic: Optional topic focus
        caption_style: Optional caption style preference
    """
    print(f"Starting AGENTIC video analysis for: {video_path}")
    
    try:
        # 1. Upload Video
        video_file = upload_to_gemini(video_path, mime_type="video/mp4")
        
        # 2. Wait for processing
        wait_for_files_active([video_file])
        
        # --- STAGE 1: DRAFTING (The Scout) ---
        print("🎬 Stage 1: The Scout (Drafting Candidates with Gemini 2.0 Flash)...")
        # Prepare prompt
        transcript_text = None
        if transcript_path and os.path.exists(transcript_path):
            try:
                print(f"Reading transcript from {transcript_path}")
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read()
            except Exception as e:
                print(f"Failed to read transcript: {e}")

        # --- STAGE 1: DRAFTING (The Scout) ---
        print("🎬 Stage 1: The Scout (Drafting Candidates with Gemini 2.0 Flash)...")
        if start_time is not None:
             print(f"   Constraints: {start_time}-{end_time}s, Topic: {topic}")
             
        draft_prompt = create_draft_prompt(transcript_text, topic, start_time, end_time)
        
        draft_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[video_file, draft_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ScoutResult,
                max_output_tokens=8192,
            )
        )
        
        # Parse result into Pydantic model
        try:
             scout_result = ScoutResult(**json.loads(draft_response.text))
        except Exception as e:
            print(f"Scout parsing failed: {e}")
            with open("debug_scout_failed.json", "w") as f:
                f.write(draft_response.text)
            raise e

        candidates = scout_result.candidates
        print(f"Found {len(candidates)} candidate clips.")
        
        # --- STAGE 2: VERIFICATION (The Senior Editor) ---
        print("🕵️ Stage 2: Senior Editor (Verifying & Refining with Gemini 2.0 Flash)...")
        # Dump candidates to JSON for the next prompt
        verify_prompt = create_verification_prompt(scout_result.model_dump_json(), caption_style)
        
        final_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[video_file, verify_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VideoAnalysisResult,
                max_output_tokens=8192,
            )
        )
        
        # 4. Parse Final Response
        try:
             final_result_model = VideoAnalysisResult(**json.loads(final_response.text))
        except Exception as e:
            print(f"Final parsing failed: {e}")
            with open("debug_final_failed.json", "w") as f:
                f.write(final_response.text)
            raise e
        final_dict = final_result_model.model_dump()
        
        # --- 5. Post-Processing: Duration Filter ---
        # Strictly filter out short clips that bypassed the prompt
        valid_clips = []
        print("\n🔍 Running Duration Filter on Candidates:")
        for clip in final_dict.get('selected_clips', []):
            duration = clip.get('refined_duration', 0)
            start = clip.get('refined_start', 0)
            end = clip.get('refined_end', 0)
            derived_duration = end - start
            
            print(f"   Checking Clip {clip.get('clip_id')}: Start={start:.2f}, End={end:.2f}, Derived={derived_duration:.2f}s, Explicit={duration:.2f}s")
            
            # Check for sanity
            if derived_duration < 10.0:
                 print(f"   ❌ Dropping - Derived Duration too short (<10s)")
                 continue
                 
            if duration < 10.0:
                 print(f"   ❌ Dropping - Explicit Duration too short (<10s)")
                 continue
            
            # Ensure duration is consistent
            if abs(duration - derived_duration) > 1.0:
                print(f"   ⚠️ Adjusting duration from {duration} to {derived_duration}")
                clip['refined_duration'] = derived_duration
                
            valid_clips.append(clip)
            print(f"   ✅ Clip kept.")
            
        if not valid_clips:
            print("❌ ALL clips were filtered out due to duration/quality constraints. Returning raw candidates as fallback.")
            # Fallback to candidates if everything is filtered?
            # Or just return empty list and let UI handle "No clips found"?
            # Better to show nothing than bad clips.
        
        final_dict['selected_clips'] = valid_clips
        print(f"Post-Filter Count: {len(valid_clips)} clips.\n")
        
        # --- NEW: Generate Thumbnails for Videos too ---
        print("Generating viral thumbnails for video clips...")
        from image_generator import generate_viral_thumbnail

        for clip in final_dict.get('selected_clips', []):
            try:
                print(f"Generating thumbnail for video clip: {clip['clip_id']}")
                # Use viral reasoning or description
                visual_prompt = clip.get('description') or clip.get('reasoning') or "Viral video moment"
                
                # We don't have explicit topic metadata here usually, so infer or generic
                thumb_path = generate_viral_thumbnail(visual_prompt, "Video Content")
                if thumb_path:
                    clip['thumbnail_path'] = thumb_path
            except Exception as img_err:
                print(f"Failed to generate thumbnail for {clip.get('clip_id')}: {img_err}")
        
        final_count = len(final_dict.get('selected_clips', []))
        print(f"Analysis complete! Final Approved Clips: {final_count}")
        return final_dict
            
    except Exception as e:
        print(f"Video analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
