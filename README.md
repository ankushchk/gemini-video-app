# AI Viral Shorts Generator

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18+-61DAFB.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-orange)

## Project Overview

This application is an automated video processing pipeline designed to transform long-form video content (such as podcasts, interviews, and vlogs) into engaging, vertical short-form clips suitable for platforms like TikTok, Instagram Reels, and YouTube Shorts.

It leverages Google's Gemini 2.0 Flash multimodal AI to analyze video content, identify high-potential "viral" moments based on context and engagement, and automatically edit these segments. The system includes features for smart face tracking to keep speakers centered, AI-generated captions, and a comprehensive review dashboard for final touches.

## Key Features

- **Agentic AI Analysis**: Utilizes a two-stage AI pipeline ("Scout" and "Senior Editor") to scan videos for the best hooks and verify their viral potential.
- **Smart Face Cropping**: automatically detects active speakers using MediaPipe and dynamically crops the video to a 9:16 vertical aspect ratio, keeping the subject centered.
- **AI Captions**: Generates accurate captions with word-level highlighting for maximum viewer retention.
- **Interactive Dashboard**: A web-based interface to review, edit, and refine clips before final export.
- **User-Controlled Editing**:
    - **Timeline Editor**: Fine-tune the start and end times of each clip with precision.
    - **Subtitle Editor**: Manually correct transcript text, adjust timing, and customize caption burn-in.
- **High-Performance Rendering**: Powered by FFmpeg for professional-grade video processing and rendering.
- **Spam Filter**: Automatically filters out clips shorter than 15 seconds to ensure content quality.

## System Architecture

The following diagram illustrates the data flow from video upload to final clip generation:

![System Architecture](./mermaid.svg)

1.  **User Interface**: The React frontend handles file uploads and user interaction.
2.  **API Layer**: The FastAPI backend receives the video and orchestrates the analysis.
3.  **Analysis Engine**: The backend sends video data to Google Gemini 2.0 Flash, which returns a structured list of candidate clips.
4.  **Rendering Engine**: Selected clips are processed by FFmpeg. MediaPipe is used for face detection coordinates, which inform the crop filter. Captions are generated as soft subtitles or burned in.
5.  **Feedback Loop**: Users can review the generated clips and trigger re-renders with adjusted parameters.

## Technology Stack

- **Frontend**:
    - React 18+
    - TypeScript
    - TailwindCSS (Styling)
    - Vite (Build Tool)
    - Lucide React (Icons)

- **Backend**:
    - Python 3.10+
    - FastAPI (Web Framework)
    - Uvicorn (ASGI Server)
    - Pydantic (Data Validation)

- **AI & Processing**:
    - Google Gemini 2.0 Flash (via `google-genai` SDK)
    - FFmpeg (Video Manipulation)
    - OpenCV (Image Processing)
    - MediaPipe (Face Detection)

## Prerequisites

Before setting up the project, ensure you have the following installed on your system:

- **Python 3.10** or higher
- **Node.js 18** or higher (with npm)
- **FFmpeg**: Must be installed and accessible via the system command line (add to PATH).
- **Google Gemini API Key**: You need a valid API key from Google AI Studio.

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/viral-shorts-generator.git
cd viral-shorts-generator
```

### 2. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd backend
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

Open a new terminal window, navigate to the project root, and install Node.js dependencies:

```bash
npm install
```

### 4. Configuration

Create a configuration file to store your API key.

1.  Create a file named `.env` in the `backend/` directory.
2.  Add your Gemini API key to the file:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## Running the Application

You need to run both the backend API server and the frontend development server simultaneously.

### Start the Backend

In your backend terminal (with the virtual environment activated):

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

### Start the Frontend

In your frontend terminal:

```bash
npm run dev
```

The application will launch in your default web browser at `http://localhost:5173`.

## Usage Guide

1.  **Select Video Source**: On the dashboard, you can either drag and drop an MP4 file or paste a YouTube URL.
2.  **Configure Analysis**: Optionally, specify a "Topic Focus" (e.g., "Funny moments", "Technical explanation") to guide the AI.
3.  **Analyze**: Click the "Analyze Video" button. The process may take 1-3 minutes depending on video length.
4.  **Review Results**: Once analysis is complete, you will see a grid of generated clips.
    - **Viral Score**: Indicates the predicted engagement level.
    - **Reasoning**: Explains why the AI selected this segment.
5.  **Edit Clip**:
    - Click "Watch Reel" to preview the generated vertical video.
    - Click "Edit Captions" to open the subtitle editor. make changes to text or timing, and click "Save & Burn" to re-render the video.
6.  **Download**: Click the download icon on the video player to save the final MP4 file to your device.

## Project Structure

- `backend/main.py`: The entry point for the FastAPI application.
- `backend/video_analyzer.py`: Contains the logic for interacting with Gemini and parsing the analysis results.
- `backend/video_renderer.py`: Handles all FFmpeg operations, including cropping, resizing, and subtitle embedding.
- `backend/face_tracker.py`: Implements the MediaPipe face detection logic.
- `src/App.tsx`: The main React component structure.
- `src/ContentFactory.tsx`: The core component for displaying and managing generated clips.

## Contributing

Contributions are welcome. Please ensure that any pull requests include a detailed description of changes and test cases where applicable.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
