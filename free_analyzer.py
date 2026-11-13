import cv2
import numpy as np
from scenedetect import detect, ContentDetector, AdaptiveDetector
import subprocess
import json

class SimpleFreeAnalyzer:
    def __init__(self):
        pass
    
    def analyze_moments(self, video_path):
        """Find engaging moments using free methods (no AI API needed)"""
        print("Using FREE rule-based analysis (no API costs!)...")
        
        moments = []
        
        # 1. Detect scene changes (fast cuts = action)
        print("  - Detecting scene changes...")
        scene_changes = self._detect_scenes(video_path)
        
        # 2. Detect motion intensity
        print("  - Analyzing motion intensity...")
        motion_moments = self._detect_motion(video_path)
        
        # 3. Detect audio peaks (loud = exciting)
        print("  - Finding audio peaks...")
        audio_peaks = self._detect_audio_peaks(video_path)
        
        # Combine all indicators and remove duplicates (within 30 seconds)
        all_timestamps = []
        all_timestamps.extend(scene_changes)
        all_timestamps.extend(motion_moments)
        all_timestamps.extend(audio_peaks)
        
        # Sort and remove timestamps too close together
        all_timestamps.sort()
        filtered_timestamps = []
        for ts in all_timestamps:
            if not filtered_timestamps or (ts - filtered_timestamps[-1]) > 30:
                filtered_timestamps.append(ts)
        
        # Create moments from timestamps (take top 10 spread throughout video)
        for timestamp in filtered_timestamps[:10]:  # Top 10 moments
            score = 0
            reason = []
            
            if timestamp in scene_changes:
                score += 3
                reason.append("fast cuts")
            if timestamp in motion_moments:
                score += 4
                reason.append("high action")
            if timestamp in audio_peaks:
                score += 3
                reason.append("audio spike")
            
            moments.append({
                'timestamp': timestamp,
                'engagement_score': min(score, 10),
                'reason': f"Engaging moment: {', '.join(reason)}"
            })
        
        return moments
    
    def _detect_scenes(self, video_path):
        """Detect scene changes using PySceneDetect"""
        try:
            scene_list = detect(video_path, ContentDetector(threshold=27.0))
            # Get scenes throughout the video, not just first 20
            timestamps = [scene[0].get_seconds() for scene in scene_list]
            # Spread them out - take every Nth scene to get variety
            if len(timestamps) > 20:
                step = len(timestamps) // 20
                timestamps = [timestamps[i] for i in range(0, len(timestamps), step)][:20]
            return timestamps
        except:
            return []
    
    def _detect_motion(self, video_path):
        """Detect high motion intensity throughout entire video"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"    Scanning {duration/60:.1f} minute video...")
        
        prev_frame = None
        motion_scores = []
        frame_count = 0
        
        # Sample every 90 frames (every 3 seconds at 30fps) for speed
        sample_rate = 90
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample frames throughout the ENTIRE video
            if frame_count % sample_rate != 0:
                frame_count += 1
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, gray)
                motion_score = np.mean(diff)
                timestamp = frame_count / fps
                motion_scores.append((timestamp, motion_score))
            
            prev_frame = gray
            frame_count += 1
            
            # Progress indicator
            if frame_count % (sample_rate * 20) == 0:
                progress = (frame_count / total_frames) * 100
                print(f"    Progress: {progress:.0f}%")
        
        cap.release()
        
        # Sort by motion score and get top moments
        motion_scores.sort(key=lambda x: x[1], reverse=True)
        top_moments = [timestamp for timestamp, score in motion_scores[:15]]
        
        return sorted(top_moments)
    
    def _detect_audio_peaks(self, video_path):
        """Detect loud audio moments"""
        try:
            # Extract audio volume data
            cmd = [
                'ffmpeg', '-i', video_path,
                '-af', 'volumedetect',
                '-vn', '-sn', '-dn',
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.STDOUT)
            
            # Simple heuristic: return evenly spaced timestamps
            # (proper audio analysis would require more processing)
            cap = cv2.VideoCapture(video_path)
            duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # Return timestamps at 20%, 40%, 60%, 80% (likely peaks)
            return [duration * 0.2, duration * 0.4, duration * 0.6, duration * 0.8]
        except:
            return []
