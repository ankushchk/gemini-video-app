
"""
Face Tracker Module using MediaPipe
Centers the active speaker for vertical video cropping.
"""
import cv2
import mediapipe as mp
import numpy as np
# Explicitly import solutions to avoid attribute errors
from mediapipe.python.solutions import face_detection

class FaceTracker:
    def __init__(self):
        self.mp_face_detection = face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, # 0 for close range, 1 for far range (5 meters)
            min_detection_confidence=0.6
        )
        
    def analyze_video(self, video_path: str, sample_rate: int = 5):
        """
        Analyzes video and returns a list of (timestamp, center_x) for each frame.
        sample_rate: Analyze every Nth frame to save time.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video file {video_path}")
            return []

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        centering_data = [] # List of {'frame': i, 'timestamp': t, 'center_x': x}
        
        frame_idx = 0
        print(f"Tracking faces in {video_path}...")
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
                
            # Only process every Nth frame
            if frame_idx % sample_rate == 0:
                # Convert the BGR image to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(image)
                
                center_x = 0.5 # Default to center
                
                if results.detections:
                    # Find the largest face (assuming it's the active speaker)
                    max_area = 0
                    primary_detection = None
                    
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        area = bbox.width * bbox.height
                        if area > max_area:
                            max_area = area
                            primary_detection = detection
                    
                    if primary_detection:
                        bbox = primary_detection.location_data.relative_bounding_box
                        # Calculate center x (relative 0.0 to 1.0)
                        raw_center_x = bbox.xmin + (bbox.width / 2)
                        center_x = max(0.0, min(1.0, raw_center_x))
                
                timestamp = frame_idx / fps
                centering_data.append({
                    'frame': frame_idx,
                    'timestamp': timestamp,
                    'center_x': center_x
                })
                
            frame_idx += 1
            if frame_idx % 100 == 0:
                print(f"Processed {frame_idx}/{total_frames} frames...")

        cap.release()
        
        # Post-process: Interpolate missing frames and smooth
        return self._smooth_camera_path(centering_data, total_frames, sample_rate)

    def _smooth_camera_path(self, data, total_frames, sample_rate):
        """
        Interpolates the sparse analysis data to per-frame data and applies smoothing.
        """
        if not data:
             return [0.5] * total_frames

        # unzipping
        frames = [d['frame'] for d in data]
        centers = [d['center_x'] for d in data]
        
        # interpolate to fill all frames
        all_frames = np.arange(total_frames)
        interpolated_centers = np.interp(all_frames, frames, centers)
        
        # Apply smoothing (Moving Average)
        window_size = 30 # Approx 1 second at 30fps
        smoothed_centers = np.convolve(
            interpolated_centers, 
            np.ones(window_size)/window_size, 
            mode='same'
        )
        
        return smoothed_centers

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        tracker = FaceTracker()
        path = sys.argv[1]
        results = tracker.analyze_video(path)
        print(f"Generated {len(results)} plot points. First 10:", results[:10])
