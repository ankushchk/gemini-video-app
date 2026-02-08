
import re
import requests
import yt_dlp
import os
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def download_youtube_video(video_url: str, output_dir: str = "uploads") -> str | None:
    """
    Downloads a YouTube video using yt-dlp.
    Returns the path to the downloaded file.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_id = info['id']
            ext = info['ext']
            return f"{output_dir}/{video_id}.{ext}"
            
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def get_video_metadata(video_url: str) -> dict | None:
    """
    Fetches video metadata (title, duration, thumbnail) without downloading.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {
                'title': info.get('title'),
                'duration': info.get('duration'), # seconds
                'thumbnail': info.get('thumbnail'),
                'author': info.get('uploader'),
                'video_id': info.get('id')
            }
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return None

def get_video_title(video_url: str) -> str | None:
    """
    Fetches the video title using YouTube's oEmbed endpoint.
    """
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={video_url}&format=json"
        response = requests.get(oembed_url)
        if response.status_code == 200:
            data = response.json()
            return data.get('title')
        return None
    except Exception as e:
        print(f"Error fetching video title: {e}")
        return None

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
