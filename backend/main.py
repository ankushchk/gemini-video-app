from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil

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
    # Save the file locally so the Gemini Agent can 'Scout' it later
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze video
    try:
        from scout_agent import analyze_video
        analysis_result = analyze_video(file_location)
        
        # Clean up the string to ensure it's valid JSON if needed, or just return it
        # The prompt asks for JSON, so we expect a JSON string.
        # Let's try to parse it to ensure it is valid JSON before returning
        import json
        import re
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)