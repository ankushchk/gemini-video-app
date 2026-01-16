import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# 1. Setup Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_video(video_path):
    # 2. Upload Video to Gemini File API
    # Gemini 3 handles up to 1 hour of video (~1M tokens)
    print("Uploading video...")
    video_file = client.files.upload(file=video_path)
    
    # 3. Request Analysis with High Thinking
    print("Analyzing for viral hooks...")
    prompt = """
    Analyze this 1-hour video. Identify 10 viral hooks. 
    For each hook, provide:
    - Start and End Timestamps (HH:MM:SS)
    - A 'Viral Score' from 1-10
    - A brief reason why it will go viral.
    Return the result in valid JSON format.
    """
    
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    from google.genai.errors import ClientError

    @retry(
        retry=retry_if_exception_type(ClientError),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60)
    )
    def generate_with_retry():
        return client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[video_file, prompt],
            config=types.GenerateContentConfig(
                # THIS IS THE KEY FOR GEMINI 3 HACKATHONS
                thinking_config=types.ThinkingConfig(thinking_level="HIGH")
            )
        )

    try:
        response = generate_with_retry()
        return response.text
    except Exception as e:
        print(f"Failed after retries: {e}")
        return str(e)

# Example usage:
# print(analyze_video("podcast_episode_01.mp4"))