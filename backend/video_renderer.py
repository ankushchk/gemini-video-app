import ffmpeg
import os
import json

FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"

def hex_to_ffmpeg_color(hex_color):
    """Converts hex #RRGGBB to FFmpeg color string 0xRRGGBB"""
    if hex_color.startswith("#"):
        return f"0x{hex_color[1:]}FF" # Add alpha
    return "white"

def generate_srt_content(captions: list, time_offset: float = 0.0) -> str:
    """Generates SRT formatted string from captions.
    time_offset: Adjust timestamps by subtracting this value (e.g. clip start time).
    Automatically detects if captions are already relative to 0.
    """
    if not captions:
        return ""

    # Smart Detection: Are timestamps absolute or relative?
    # If the first caption starts at 1.0s, but time_offset is 120.0s, 
    # then timestamps are likely ALREADY relative.
    # If first caption starts at 121.0s, they are absolute.
    
    first_cap_start = float(captions[0].get('start_offset', 0))
    avg_cap_start = sum(float(c.get('start_offset', 0)) for c in captions[:5]) / min(len(captions), 5)
    
    # Heuristic: If average caption start is much less than the offset (clip start),
    # AND the offset is significant (e.g. > 10s), assume relative.
    # We use a margin of 5 seconds to be safe (in case clip starts at 10s and first caption is at 0s).
    effective_offset = time_offset
    if time_offset > 10.0 and avg_cap_start < (time_offset - 5.0):
        print(f"   ℹ️ Captions appear to be RELATIVE (Avg Start {avg_cap_start:.1f}s vs Clip Start {time_offset:.1f}s). Ignoring offset.")
        effective_offset = 0.0
    else:
        print(f"   ℹ️ Captions appear to be ABSOLUTE (Avg Start {avg_cap_start:.1f}s vs Clip Start {time_offset:.1f}s). Applying offset -{time_offset:.1f}s.")

    srt_output = ""
    for i, cap in enumerate(captions, 1):
        # Default to 0 if missing
        cap_start = float(cap.get('start_offset', 0))
        cap_end = float(cap.get('end_offset', 0))
        
        # Adjust for clip start time
        start = max(0.0, cap_start - effective_offset)
        end = max(0.0, cap_end - effective_offset)
        
        text = cap.get('text', '')
        
        # Format seconds to HH:MM:SS,mmm
        def fmt_time(t):
            hours = int(t // 3600)
            minutes = int((t % 3600) // 60)
            seconds = int(t % 60)
            millis = int((t * 1000) % 1000)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
            
        srt_output += f"{i}\n{fmt_time(start)} --> {fmt_time(end)}\n{text}\n\n"
    return srt_output

def render_video_clip(source_path: str, clip_data: dict, output_path: str):
    """
    Renders a video clip with embedded soft subtitles.
    """
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source video not found: {source_path}")
            
        # Parse timing
        start = float(clip_data.get('refined_start', clip_data.get('start', 0)))
        end = float(clip_data.get('refined_end', clip_data.get('end', start + 60)))
        duration = end - start
        
        print(f"Rendering clip: {start}s -> {end}s ({duration}s)")
        
        # 1. Video & Audio Input (Trimmed)
        # We use explicit trimming on input to ensure sync
        input_stream = ffmpeg.input(source_path, ss=start, t=duration)
        video = input_stream.video
        audio = input_stream.audio
        
        # 2. Generate Subtitles (SRT)
        captions = clip_data.get('captions', [])
        subtitle_input = None
        temp_srt_path = output_path + ".srt"
        
        if captions:
            print(f"Embedding {len(captions)} captions as soft subtitles...")
            srt_content = generate_srt_content(captions, time_offset=start)
            with open(temp_srt_path, "w") as f:
                f.write(srt_content)
            subtitle_input = ffmpeg.input(temp_srt_path)
        
        # 3. Output
        # Combine video, audio, and subtitles (if any)
        streams = [video, audio]
        kwargs = {
            'vcodec': 'libx264', 
            'acodec': 'aac', 
            'strict': 'experimental'
        }
        
        if subtitle_input:
            streams.append(subtitle_input)
            kwargs['scodec'] = 'mov_text' # Valid subtitle codec for MP4 container
            
        out = ffmpeg.output(*streams, output_path, **kwargs)
        out = out.overwrite_output()
        
        print("Running FFmpeg render...")
        out.run(capture_stdout=True, capture_stderr=True)
        
        # Cleanup temp srt
        if os.path.exists(temp_srt_path):
            os.remove(temp_srt_path)
            
        print(f"Render complete: {output_path}")
        return output_path
        
    except ffmpeg.Error as e:
        error_log = e.stderr.decode('utf8')
        print(f"FFmpeg Render Error: {error_log}")
        raise Exception(f"Render failed: {error_log}")
    except Exception as e:
        print(f"General Error: {e}")
        raise e


def render_vertical_video(source_path: str, clip_data: dict, output_path: str):
    """
    Renders a 9:16 vertical video with blur-fill background.
    Uses Smart Face Crop (Static Average) to keep speaker in frame.
    No captions burned in (handled by frontend).
    """
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source video not found: {source_path}")
            
        start = float(clip_data.get('refined_start', clip_data.get('start', 0)))
        end = float(clip_data.get('refined_end', clip_data.get('end', start + 60)))
        duration = end - start
        
        print(f"Rendering VERTICAL clip: {start}s -> {end}s ({duration}s)")
        
        # --- SMART FACE DETECTION ---
        # 1. Extract a temporary clip to analyze just this segment (fast)
        temp_cut_path = output_path + ".temp_cut.mp4"
        
        # Determine crop x-offset
        crop_x_center = 0.5 # Default to center
        
        try:
             # Fast stream copy trim
             # Note: -ss before -i is fast but keyframe dependent. For analysis it's okay.
             # Ideally we analyze the source file with seek, but creating a small temp file is safer for MediaPipe.
             stream_cut = ffmpeg.input(source_path, ss=start, t=duration)
             stream_cut = ffmpeg.output(stream_cut, temp_cut_path, c='copy', loglevel='error')
             stream_cut.run(overwrite_output=True)
             
             # Analyze
             print("🧠 Analyzing face position for Smart Crop...")
             from face_tracker import FaceTracker
             tracker = FaceTracker()
             # We just need a quick analysis, sample every 10 frames
             centers = tracker.analyze_video(temp_cut_path, sample_rate=10)
             
             if centers:
                 import numpy as np
                 # Use median to ignore outliers/glitches
                 crop_x_center = float(np.median(centers))
                 print(f"🎯 Smart Crop detected face center at: {crop_x_center:.2f}")
             else:
                 print("⚠️ No face detected, falling back to center crop.")
                 
             # Cleanup temp
             if os.path.exists(temp_cut_path):
                 os.remove(temp_cut_path)
                 
        except Exception as e:
            print(f"Smart Crop failed (fallback to center): {e}")

        # --- RENDER ---
        
        # Input Stream (Trimmed)
        input_stream = ffmpeg.input(source_path, ss=start, t=duration)
        vid = input_stream.video
        aud = input_stream.audio
        
        # Get video info for dimensions
        probe = ffmpeg.probe(source_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        
        # Background: Scale huge, crop center, blur
        # We need to ensure aspect ratio is maintained. 
        # 1080x1920 (9:16). Source is likely 16:9 (e.g. 1920x1080)
        # To fill 1920 height, we need scale factor = 1920 / 1080 = 1.777
        # New width = 1920 * 1.777 = 3413
        bg = vid.filter('scale', 3414, 1920).filter('crop', 1080, 1920).filter('boxblur', luma_radius=20, luma_power=1)
        
        # Foreground: Smart Crop + Scale
        # Target: 1080px width, auto height
        # But we want to crop a 9:16 vertical slice FIRST? 
        # No, commonly we take the full height (1080) and a 9:16 width (1080 * 9/16 = 607px)
        # OR we just scale the whole thing to width 1080 and have letterboxing?
        # NO, Opus style is: Crop a vertical slice of the original video (focusing on face), then scale it up.
        
        # Strategy:
        # 1. Crop a 9:16 aspect ratio slice from the original 1080p source.
        #    Target slice height = 1080 (full height)
        #    Target slice width = 1080 * (9/16) = 607.5 => 608px
        #    Center X = crop_x_center * 1920
        #    Crop X = Center X - (608 / 2)
        
        target_crop_h = height # 1080
        target_crop_w = int(height * (9/16)) # 607
        
        # Calculate x coordinate
        # Ensure we don't go out of bounds
        center_pixel = crop_x_center * width
        crop_x = int(center_pixel - (target_crop_w / 2))
        crop_x = max(0, min(width - target_crop_w, crop_x)) # Clamp
        
        print(f"Applying Crop: {target_crop_w}x{target_crop_h} at x={crop_x}")
        
        # Crop then scale to 1080 width (to fit the output canvas 1080x1920)
        fg = vid.filter('crop', target_crop_w, target_crop_h, crop_x, 0).filter('scale', 1080, 1920)
        
        # Wait, if we scale to 1080x1920, we don't need a background!
        # Opus usually does this: Full screen vertical video.
        # So we just output 'fg' effectively.
        # BUT, if we want the "blur fill" effect (which is safer if resolution is low), we keep the background layer.
        # Actually, scaling 608x1080 source to 1080x1920 is a 1.77x zoom. It might be blurry.
        # But that's what Reel format demands.
        
        # Let's output just the FG scaled up. It looks cleaner.
        # If user wants blur fill, we can add it later. For "Perfect" reels, full screen is better.
        
        # --- Burned-In Subtitles ---
        captions = clip_data.get('captions', [])
        temp_srt_path = output_path + ".srt"
        
        # Soft Subtitles Fallback (mov_text)
        # Since FFmpeg binary lacks libass (subtitles) and libfreetype (drawtext), 
        # we embed soft subtitles into the container stream.
        subtitle_input = None
        if captions:
            print(f"Embedding {len(captions)} captions as SOFT subtitles (mov_text)...")
            srt_content = generate_srt_content(captions, time_offset=start)
            with open(temp_srt_path, "w") as f:
                f.write(srt_content)
            subtitle_input = ffmpeg.input(temp_srt_path)

        streams = [fg, aud]
        kwargs = {
            'vcodec': 'libx264', 
            'acodec': 'aac', 
            'strict': 'experimental'
        }
        
        if subtitle_input:
            streams.append(subtitle_input)
            kwargs['scodec'] = 'mov_text' 

        out = ffmpeg.output(*streams, output_path, **kwargs)
        out = out.overwrite_output()
        
        print("Running FFmpeg Vertical Render...")
        out.run(capture_stdout=True, capture_stderr=True)
        
        print(f"Vertical Render complete: {output_path}")
        return output_path
        
    except ffmpeg.Error as e:
        error_log = e.stderr.decode('utf8')
        print(f"FFmpeg Render Error: {error_log}")
        raise Exception(f"Render failed: {error_log}")
    except Exception as e:
        print(f"General Error: {e}")
        import traceback
        traceback.print_exc()
        raise e
