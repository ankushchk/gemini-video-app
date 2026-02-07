import ffmpeg
import os

def cut_video_clip(video_path: str, start_time: float, end_time: float, output_path: str):
    """
    Cuts a clip from a video file.
    
    Args:
        video_path: Path to source video
        start_time: Start time in seconds
        end_time: End time in seconds
        output_path: Path to save the clip
    """
    try:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Source video not found: {video_path}")
            
        print(f"Cutting clip from {start_time} to {end_time}...")
        
        (
            ffmpeg
            .input(video_path, ss=start_time, to=end_time)
            .output(output_path, c='copy') # 'c=copy' is fast (stream copy) but might be less precise. 
            # If precision issues, remove c='copy' to re-encode (slower but frame-perfect)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        print(f"Clip saved to: {output_path}")
        return output_path
        
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
        raise Exception(f"Failed to cut clip: {e.stderr.decode('utf8')}")
