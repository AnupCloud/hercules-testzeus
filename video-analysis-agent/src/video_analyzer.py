"""
Video Analyzer

Analyzes video recordings to detect visible actions and events.
"""

import cv2
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np


class VideoAnalyzer:
    """Analyzes video recordings of test execution"""
    
    def __init__(self, video_path: str, config: Optional[Dict] = None):
        self.video_path = Path(video_path)
        self.config = config or {}
        self.frame_skip = self.config.get('frame_skip', 30)  # Analyze every Nth frame
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze video(s) to detect actions.
        
        Returns:
            Dictionary containing:
            - video_count: int
            - detected_events: List[Dict]
            - timestamps: List[float]
        """
        videos = self._get_video_files()
        
        all_events = []
        for video_file in videos:
            events = self._analyze_single_video(video_file)
            all_events.extend(events)
        
        return {
            'video_count': len(videos),
            'detected_events': all_events,
            'total_events': len(all_events)
        }
    
    def _get_video_files(self) -> List[Path]:
        """Get list of video files to analyze"""
        if self.video_path.is_file():
            return [self.video_path]
        elif self.video_path.is_dir():
            # Find all video files in directory
            video_extensions = ['.webm', '.mp4', '.avi', '.mov']
            return [f for f in self.video_path.iterdir() if f.suffix.lower() in video_extensions]
        else:
            return []
    
    def _analyze_single_video(self, video_file: Path) -> List[Dict[str, Any]]:
        """
        Analyze a single video file.
        
        This is a simplified implementation. A production version would use:
        - OCR to detect text changes
        - Object detection to identify UI elements
        - Scene change detection
        - Mouse/click detection
        """
        events = []
        
        try:
            cap = cv2.VideoCapture(str(video_file))
            if not cap.isOpened():
                print(f"Warning: Could not open video {video_file}")
                return events
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            print(f"   Analyzing {video_file.name}: {duration:.1f}s, {frame_count} frames")
            
            frame_idx = 0
            prev_frame = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Only analyze every Nth frame
                if frame_idx % self.frame_skip == 0:
                    timestamp = frame_idx / fps if fps > 0 else 0
                    
                    # Detect scene changes (simplified)
                    if prev_frame is not None:
                        diff = cv2.absdiff(frame, prev_frame)
                        change_score = np.mean(diff)
                        
                        if change_score > 30:  # Threshold for significant change
                            events.append({
                                'video': video_file.name,
                                'timestamp': round(timestamp, 2),
                                'type': 'scene_change',
                                'description': f'Significant UI change detected',
                                'confidence': min(change_score / 100, 1.0)
                            })
                    
                    prev_frame = frame.copy()
                
                frame_idx += 1
            
            cap.release()
            
        except Exception as e:
            print(f"Error analyzing video {video_file}: {e}")
        
        return events
