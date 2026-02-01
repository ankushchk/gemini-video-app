"""
Podcast Analyzer - 6-Stage Analysis Pipeline
Uses Gemini 3 Pro with HIGH thinking for deep editorial reasoning
"""
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ClientError

load_dotenv()

# Setup Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def create_analysis_prompt(transcript_entries: list, metadata: dict = None) -> str:
    """
    Create comprehensive prompt for 6-stage podcast analysis
    
    Args:
        transcript_entries: List of transcript entries with timestamps, speakers, text
        metadata: Optional dict with guest, topic, tone
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
    
    prompt = f"""You are a podcast content analyzer and viral clip strategist. Your role is to identify high-impact moments from podcast transcripts and plan their transformation into short-form vertical video content.

{context}

## TRANSCRIPT:
{transcript_text}

---

## YOUR TASK:

Analyze this podcast transcript through 6 stages and return a comprehensive JSON response.

### STAGE 1: Semantic Chunking
Parse the transcript into coherent segments (30–90 seconds each).

**Chunking Rules:**
- Preserve complete thoughts and stories
- Break at natural conversation pauses
- Never split mid-anecdote or mid-argument
- Each chunk should be self-contained

For each chunk, provide:
- start_time (seconds)
- end_time (seconds)
- speakers (array of speaker names)
- summary (1-2 sentence description)

---

### STAGE 2: Viral Potential Analysis
For each chunk, evaluate viral potential.

**Content Signals to Assess:**
- Emotional peak (surprise, laughter, insight, controversy)
- Quotability (memorable one-liner or soundbite)
- Contrarian angle (challenges common wisdom)
- Storytelling structure (setup → tension → payoff)
- Standalone clarity (makes sense without context)

**Platform Fit:**
- Strong hook in first 3 seconds
- Holds attention through 60 seconds
- Invites engagement (comments, shares)

**Scoring:**
- Assign viral_score: 0.0–1.0 (where 1.0 is maximum viral potential)
- Provide editorial_reasoning (2–3 sentences explaining the score)
- Flag context_dependency (true/false - does it need prior context?)

---

### STAGE 3: Clip Refinement
Select the top 3-5 chunks with highest viral scores and refine them.

**Timing Adjustments:**
- Tighten intro (cut filler words, setup fluff)
- Preserve core insight/punchline
- End on strong closing beat
- Target 30–60 seconds (platform sweet spot)

Provide refined:
- refined_start (seconds)
- refined_end (seconds)
- refined_duration (seconds)

---

### STAGE 4: Platform Optimization
For each selected clip, generate platform-optimized content.

**1. Hook (first 3 seconds)**
- Pattern interrupt or provocative statement
- Can be direct quote, question, or tension-builder
- Example: "I lost $2M before I learned this..."

**2. Captions (on-screen text)**
- Break speech into 3–7 word chunks
- Emphasize key words with CAPS or markers
- Array of caption objects with: text, start_offset, end_offset, emphasis (array of emphasized words)

**3. Reel Caption**
- 1–2 sentence summary
- Include 1–2 open-ended questions to drive comments

**4. Hashtags**
- 5–8 hashtags (mix of broad and niche)

**5. Tone Adaptation**
- pacing: "slow-burn" | "rapid-fire" | "conversational"
- music_vibe: "energetic" | "reflective" | "tense" | "inspiring"

---

### STAGE 5: Visual Treatment Plan
Design a minimal, repeatable visual system for each clip.

**Visual Beats (3–5 per clip):**
Each beat specifies:
- image_concept: Abstract texture, symbolic object, or contextual scene
  - Example: "Close-up of coffee cup on table" (grounding, casual)
  - Example: "Abstract light rays" (insight, realization)
- text_overlay: Which quote/keyword appears
- motion: "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "fade" | "static"
- motion_intensity: 2-5% for subtle, 5-10% for moderate
- duration: 5–15 seconds

**Style Consistency:**
- color_palette: Array of 2–3 hex colors
- typography: Font style description
- composition: "rule-of-thirds" | "centered" | "lower-third"

---

### STAGE 6: Assembly Specification
Provide technical build plan for each clip.

**Technical Specs:**
- aspect_ratio: "9:16"
- resolution: "1080x1920"
- fps: 30
- audio_format: "AAC"
- video_codec: "H.264"

**Layer Structure (in order):**
1. background_layer: "image" | "gradient" | "solid-color"
2. audio_waveform: true/false (subtle visualization)
3. captions_layer: Animated text
4. hook_overlay: First 3 seconds

**Motion Choreography:**
- image_transition: "cross-dissolve" | "cut"
- transition_duration: 0.5 seconds
- text_animation: "fade-in" | "slide-up" | "typewriter"

---

## OUTPUT FORMAT:

Return ONLY valid JSON (no markdown, no code blocks) in this exact structure:

```json
{{
  "chunks": [
    {{
      "chunk_id": "chunk_01",
      "start_time": 15.0,
      "end_time": 68.0,
      "duration": 53.0,
      "speakers": ["Joe Rogan", "Elon Musk"],
      "summary": "Discussion about AI's transformative potential"
    }}
  ],
  "analysis": [
    {{
      "chunk_id": "chunk_01",
      "viral_score": 0.87,
      "editorial_reasoning": "Strong contrarian take comparing AI to fire. Quotable moment with clear emotional peak. Works standalone.",
      "context_dependency": false,
      "emotional_peak": "insight",
      "quotability": "It's more profound than electricity or fire",
      "platform_fit": "Excellent hook potential, holds attention, invites debate"
    }}
  ],
  "selected_clips": [
    {{
      "clip_id": "clip_01",
      "chunk_id": "chunk_01",
      "start": 15.0,
      "end": 68.0,
      "refined_start": 17.0,
      "refined_end": 62.0,
      "refined_duration": 45.0,
      "viral_score": 0.87,
      "reasoning": "Top viral potential due to provocative comparison and quotable insight",
      
      "hook": "AI is more profound than fire or electricity",
      
      "captions": [
        {{
          "text": "AI is MORE PROFOUND",
          "start_offset": 0.0,
          "end_offset": 2.5,
          "emphasis": ["MORE PROFOUND"]
        }},
        {{
          "text": "than electricity or FIRE",
          "start_offset": 2.5,
          "end_offset": 5.0,
          "emphasis": ["FIRE"]
        }}
      ],
      
      "reel_caption": "Elon Musk explains why AI is humanity's most important invention. Do you agree? 🤔",
      
      "hashtags": ["#AI", "#ElonMusk", "#Technology", "#Future", "#Innovation", "#Podcast", "#Viral", "#DeepThoughts"],
      
      "tone": {{
        "pacing": "conversational",
        "music_vibe": "reflective"
      }},
      
      "visual_beats": [
        {{
          "image_concept": "Abstract neural network visualization with glowing nodes",
          "text_overlay": "AI is more profound than fire",
          "motion": "zoom-in",
          "motion_intensity": 3,
          "duration": 8
        }},
        {{
          "image_concept": "Close-up of circuit board with warm lighting",
          "text_overlay": "It's going to amplify human capability",
          "motion": "pan-right",
          "motion_intensity": 2,
          "duration": 7
        }}
      ],
      
      "style": {{
        "color_palette": ["#1a1a2e", "#16213e", "#0f3460"],
        "typography": "Bold sans-serif, high contrast",
        "composition": "rule-of-thirds"
      }},
      
      "assembly_spec": {{
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "fps": 30,
        "audio_format": "AAC",
        "video_codec": "H.264",
        "background_layer": "image",
        "audio_waveform": true,
        "captions_layer": true,
        "hook_overlay": true,
        "image_transition": "cross-dissolve",
        "transition_duration": 0.5,
        "text_animation": "fade-in"
      }}
    }}
  ]
}}
```

CRITICAL RULES:
- Return ONLY the JSON object, no markdown formatting
- All timestamps in seconds (float)
- Viral scores between 0.0 and 1.0
- Select 3-5 clips maximum (highest viral scores)
- Be specific with visual concepts and motion details
- Ensure hooks are attention-grabbing (first 3 seconds)
- Make captions mobile-readable (3-7 words per chunk)
"""
    
    return prompt


@retry(
    retry=retry_if_exception_type(ClientError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60)
)
def analyze_podcast_with_gemini(prompt: str) -> str:
    """Call Gemini with HIGH thinking level for deep analysis"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"  # Request JSON response
        )
    )
    return response.text


def analyze_podcast(transcript_entries: list, metadata: dict = None) -> dict:
    """
    Main analysis function - runs 6-stage pipeline
    
    Args:
        transcript_entries: List of transcript entries from transcript_parser
        metadata: Optional dict with guest, topic, tone
    
    Returns:
        Complete analysis dict with all 6 stages
    """
    print("Creating analysis prompt...")
    prompt = create_analysis_prompt(transcript_entries, metadata)
    
    print("Analyzing podcast with Gemini (HIGH thinking)...")
    try:
        result_text = analyze_podcast_with_gemini(prompt)
        
        # Parse JSON response
        result = json.loads(result_text)
        
        print(f"Analysis complete! Found {len(result.get('selected_clips', []))} viral clips.")
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {result_text[:500]}...")
        # Return error structure
        return {
            "error": "Failed to parse JSON response",
            "raw_response": result_text
        }
    except Exception as e:
        print(f"Analysis failed: {e}")
        return {
            "error": str(e)
        }


# Example usage
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
