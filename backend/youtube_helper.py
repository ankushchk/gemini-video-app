
import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def extract_video_id(url: str) -> str | None:
    """
    Extracts the video ID from a YouTube URL.
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    """
    parsed = urlparse(url)
    
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
        if parsed.path.startswith('/shorts/'):
            return parsed.path.split('/')[2]
    
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    
    return None

def get_youtube_transcript(video_url: str):
    """
    Fetches the transcript for a given YouTube URL.
    Returns a list of dictionaries with 'text', 'start', and 'duration'.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    try:
        # Use instance-based API for version 1.2.4+
        api = YouTubeTranscriptApi()
        languages = ['en', 'en-US', 'en-GB']
        
        # Returns a list of FetchedTranscriptSnippet objects
        transcript_snippets = api.fetch(video_id, languages=languages)
        
        # Convert to list of dicts for compatibility
        return [
            {
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration
            }
            for snippet in transcript_snippets
        ]

    except Exception as e:
        # Fallback or specific error handling
        raise ValueError(f"No transcript available or failed to fetch: {e}")

if __name__ == "__main__":
    # Test
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    try:
        print(get_youtube_transcript(url)[:5])
    except Exception as e:
        print(f"Error: {e}")
