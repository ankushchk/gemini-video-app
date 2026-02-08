
import os
import uuid
from google import genai
from google.genai import types
import requests
from dotenv import load_dotenv

# Load env to get API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

# Directory to save generated images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_viral_thumbnail(clip_text: str, topic: str = "general", video_title: str = None) -> str | None:
    """
    Generates a viral-style thumbnail for a clip using Imagen 4 Fast.
    Returns the relative path to the saved image, or None if failed.
    """
    try:
        # Construct a punchy context
        context = f"video titled '{video_title}' about '{topic}'" if video_title else f"video about '{topic}'"
        
        # Construct a punchy prompt
        prompt = (
            f"A high-quality, viral YouTube thumbnail background for a {context}. "
            f"The image should represent this concept: '{clip_text[:100]}...'. "
            f"Style: Cinematic, high-contrast, professional, and relevant to the topic '{topic}'. "
            "Make it visually striking and emotional. 4k resolution, hyper-realistic."
        )
        
        print(f"Generating thumbnail for: {clip_text[:30]}...")
        
        # Use Imagen 4 Fast for speed and cost
        response = client.models.generate_images(
            model="imagen-4.0-fast-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9", 
                # safety_filter_level="block_medium_and_above" # Optional
            )
        )
        
        # Parse response - The SDK returns an object with generated_images
        # Each generated_image has an 'image' bytes field (if verified via debug earlier)
        # OR it might provide a URI. 
        # Based on standard Google GenAI SDK usage:
        
        if not response.generated_images:
            print("No images generated.")
            return None
            
        image_data = response.generated_images[0].image.image_bytes
        
        # Save to file
        filename = f"thumb_{uuid.uuid4().hex}.png"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(image_data)
            
        print(f"Thumbnail saved to: {filepath}")
        return filepath

    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        # import traceback
        # traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test
    path = generate_viral_thumbnail("The secret to easy cooking is heat control", "Cooking")
    print(f"Generated: {path}")
