"""
Podcast Analyzer - 6-Stage Analysis Pipeline
Uses Gemini 3 Flash Preview (latest) with native Structured Outputs for reliability
"""
import os
import json
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ClientError

load_dotenv()

# Setup Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Pydantic Models for Structured Output ---

class Segment(BaseModel):
    chunk_id: str
    start_time: float
    end_time: float
    duration: float
    speakers: List[str]
    summary: str

class AnalysisMetrics(BaseModel):
    chunk_id: str
    viral_score: float = Field(..., description="0.0 to 1.0 score indicating viral potential")
    editorial_reasoning: str
    context_dependency: bool
    emotional_peak: Optional[str] = None
    quotability: Optional[str] = None
    platform_fit: Optional[str] = None

class Caption(BaseModel):
    text: str
    start_offset: float
    end_offset: float
    emphasis: List[str]

class VisualBeat(BaseModel):
    image_concept: str
    text_overlay: Optional[str] = None
    motion: str
    motion_intensity: int
    duration: int

class Tone(BaseModel):
    pacing: str
    music_vibe: str

class Style(BaseModel):
    color_palette: List[str]
    typography: str
    composition: str

class AssemblySpec(BaseModel):
    aspect_ratio: str = "9:16"
    resolution: str = "1080x1920"
    fps: int = 30
    audio_format: str = "AAC"
    video_codec: str = "H.264"
    background_layer: str
    audio_waveform: bool
    captions_layer: bool
    hook_overlay: bool
    image_transition: str
    transition_duration: float
    text_animation: str

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
    tone: Tone
    visual_beats: List[VisualBeat]
    style: Style
    assembly_spec: AssemblySpec

class PodcastAnalysisResult(BaseModel):
    chunks: List[Segment]
    analysis: List[AnalysisMetrics]
    selected_clips: List[SelectedClip]


def create_analysis_prompt(transcript_entries: list, metadata: dict = None) -> str:
    """
    Create comprehensive prompt for 6-stage podcast analysis
    """
    
    # Format transcript for prompt
    transcript_text = ""
    for entry in transcript_entries:
        start = entry['start_time']
        speaker = entry['speaker']
        text = entry['text']
        transcript_text += f"[{int(start//60):02d}:{int(start%60):02d}] {speaker}: {text}\n"
    
    # Build metadata context
    context = ""
    if metadata:
        if metadata.get('guest'):
            context += f"Guest: {metadata['guest']}\n"
        if metadata.get('topic'):
            context += f"Topic: {metadata['topic']}\n"
        if metadata.get('tone'):
            context += f"Tone: {metadata['tone']}\n"
    
    prompt = f"""You are a podcast content analyzer and viral clip strategist.
    
{context}

## TRANSCRIPT:
{transcript_text}

---

## YOUR TASK:

Analyze this podcast transcript through 6 stages and return a comprehensive structured response.

### STAGE 1: Semantic Chunking
Parse the transcript into coherent segments (30–90 seconds each). Preserve complete thoughts.

### STAGE 2: Viral Potential Analysis
Evaluate viral potential (0.0–1.0). Look for emotional peaks, quotability, and contrarian angles.

### STAGE 3: Clip Refinement
Select the top 3-5 chunks. Tighten intro/outro. Target 30-60s.

### STAGE 4: Platform Optimization
Generate hooks, captions (with emphasis), hashtags, and social copy.

### STAGE 5: Visual Treatment Plan
Design a visual system (beats, motion, style) for each clip.

### STAGE 6: Assembly Specification
Provide technical specs for automated editing.
"""
    return prompt


@retry(
    retry=retry_if_exception_type(ClientError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30)
)
def analyze_podcast_with_gemini(prompt: str) -> PodcastAnalysisResult:
    """Call Gemini 2.0 Flash with Pydantic-based Structured Output"""
    
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PodcastAnalysisResult,
        )
    )
    
    # The response is already parsed into the Pydantic model by the SDK if using parsed fields,
    # but here we are using the standard generate_content which returns an object that can be parsed.
    # When response_schema is provided, the text is valid JSON guaranteed.
    # We can parse it into our Pydantic model.
    try:
        data = json.loads(response.text)
        return PodcastAnalysisResult(**data)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        # In case of partial failure or model hallucination on schema (rare with 2.0 flash)
        raise e


def analyze_podcast(transcript_entries: list, metadata: dict = None) -> dict:
    """
    Main analysis function
    """
    print("Creating analysis prompt...")
    prompt = create_analysis_prompt(transcript_entries, metadata)
    
    print("Analyzing podcast with Gemini 3 Flash Preview (Structured Output)...")
    try:
        # Get Pydantic model result
        result_model = analyze_podcast_with_gemini(prompt)
        
        # Convert back to dict for API response compatibility
        result_dict = result_model.model_dump()
        
        print(f"Analysis complete! Found {len(result_dict.get('selected_clips', []))} viral clips.")
        return result_dict
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e)
        }
if __name__ == "__main__":
    # Test with sample transcript entries
    sample_entries = [
        {
            'start_time': 15.0,
            'end_time': 20.0,
            'speaker': 'Joe Rogan',
            'text': "So you're telling me that AI is going to change everything?"
        },
        {
            'start_time': 20.0,
            'end_time': 28.0,
            'speaker': 'Elon Musk',
            'text': "Absolutely. I think AI is the most important thing humanity has ever worked on."
        },
        {
            'start_time': 28.0,
            'end_time': 32.0,
            'speaker': 'Joe Rogan',
            'text': "That's a bold statement. Why do you think that?"
        },
        {
            'start_time': 32.0,
            'end_time': 45.0,
            'speaker': 'Elon Musk',
            'text': "Because it's more profound than electricity or fire. It's going to amplify human capability by orders of magnitude."
        }
    ]
    
    metadata = {
        'guest': 'Elon Musk',
        'topic': 'Artificial Intelligence',
        'tone': 'Serious, thought-provoking'
    }
    
    result = analyze_podcast(sample_entries, metadata)
    print(json.dumps(result, indent=2))
