# Gemini Video App 🎥

An AI-powered tool that identifies viral hooks in long-form videos using Gemini 1.5 Pro with Reasoning (High Thinking).

## 🚀 Quick Start

### 1. Backend Setup (Python)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- Create a `.env` file in the `backend/` folder:
  ```env
  GEMINI_API_KEY=your_api_key_here
  ```
- Start the server:
  ```bash
  python3 -m uvicorn main:app --reload --port 8000
  ```

### 2. Frontend Setup (React)
```bash
# In the root directory
npm install
npm run dev
```

### 3. Usage
1. Open `http://localhost:5173`.
2. Upload a video file.
3. Wait for the Gemini "Scout" agent to analyze the video and generate viral clips.

## 🛠 Tech Stack
- **Frontend**: React, Vite, TailwindCSS, Lucide Icons.
- **Backend**: FastAPI, Google GenAI SDK (Gemini 1.5 Pro).
- **Thinking**: Uses Gemini 1.5 Pro's Reasoning capabilities for deep video analysis.
