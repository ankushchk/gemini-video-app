import ffmpeg
import os
import json

FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"

def hex_to_ffmpeg_color(hex_color):
    """Converts hex #RRGGBB to FFmpeg color string 0xRRGGBB"""
    if hex_color.startswith("#"):
        return f"0x{hex_color[1:]}FF" # Add alpha
    return "white"

def render_video_clip(source_path: str, clip_data: dict, output_path: str):
    """
    Renders a video clip with burned-in captions and effects.
    
    Args:
        source_path: Path to source video
        clip_data: standard clip JSON object (with start/end/captions)
        output_path: Path to save the rendered mp4
    """
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source video not found: {source_path}")
            
        # Parse timing
        # Prefer refined times if available
        start = float(clip_data.get('refined_start', clip_data.get('start', 0)))
        end = float(clip_data.get('refined_end', clip_data.get('end', start + 60)))
        duration = end - start
        
        print(f"Rendering clip: {start}s -> {end}s ({duration}s)")
        print(f"Burning {len(clip_data.get('captions', []))} captions...")

        # 1. Input Stream
        stream = ffmpeg.input(source_path, ss=start, t=duration)
        
        # 2. Video Filters
        # Force a standard scale to ensure drawtext behaves predictably? 
        # For now, rely on source resolution.
        
        # 3. Captions (DrawText)
        captions = clip_data.get('captions', [])
        
        for cap in captions:
            text = cap.get('text', '')
            c_start = float(cap.get('start_offset', 0))
            c_end = float(cap.get('end_offset', 5))
            
            # Escape text for FFmpeg
            # Text must be escaped: \ -> \\, ' -> \', : -> \:
            safe_text = text.replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:')
            
            # Check for emphasis (naive check)
            emphasis_words = cap.get('emphasis', [])
            is_emphatic = any(w.lower() in text.lower() for w in emphasis_words)
            
            font_color = 'yellow' if is_emphatic else 'white'
            font_size = 50 if is_emphatic else 40
            
            stream = stream.drawtext(
                text=safe_text,
                fontfile=FONT_PATH,
                fontsize=font_size,
                fontcolor=font_color,
                shadowcolor='black',
                shadowx=2,
                shadowy=2,
                x='(w-text_w)/2',      # Center horizontally
                y='h-(h/4)',          # Lower quarter
                enable=f'between(t,{c_start},{c_end})'
            )
            
        # 4. Audio Stream
        # We need to trim audio too, otherwise it might desync or take full duration
        audio = ffmpeg.input(source_path, ss=start, t=duration).audio
        
        # 5. Output
        out = ffmpeg.output(stream, audio, output_path, vcodec='libx264', acodec='aac', strict='experimental')
        out = out.overwrite_output()
        
        print("Running FFmpeg render...")
        out.run(capture_stdout=True, capture_stderr=True)
        print(f"Render complete: {output_path}")
        return output_path
        
    except ffmpeg.Error as e:
        error_log = e.stderr.decode('utf8')
        print(f"FFmpeg Render Error: {error_log}")
        raise Exception(f"Render failed: {error_log}")
