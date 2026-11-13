import whisper
import cv2
import numpy as np
from pathlib import Path
import re

class WhisperSmartAnalyzer:
    def __init__(self):
        print("Loading Whisper model (one-time download)...")
        self.model = whisper.load_model("base")  # ~150MB, runs locally
        
    def analyze_moments(self, video_path):
        """Find engaging moments using speech + motion analysis"""
        print("Using FREE Whisper + Smart Analysis...")
        
        # 1. Transcribe audio
        print("  - Transcribing audio...")
        transcript = self._transcribe_video(video_path)
        
        # 2. Find exciting moments in speech
        print("  - Finding exciting speech moments...")
        speech_moments = self._find_exciting_speech(transcript)
        
        # 3. Analyze motion at those moments
        print("  - Analyzing motion intensity...")
        motion_moments = self._analyze_motion_at_times(video_path, speech_moments)
        
        # 4. Combine and rank
        final_moments = self._rank_moments(speech_moments, motion_moments)
        
        print(f"✓ Found {len(final_moments)} upload-ready moments")
        return final_moments[:10]
    
    def _transcribe_video(self, video_path):
        """Transcribe video audio using Whisper"""
        result = self.model.transcribe(video_path)
        return result['segments']
    
    def _find_exciting_speech(self, segments):
        """Find moments with exciting keywords in speech"""
        exciting_keywords = [
            # Excitement
            r'\b(oh my god|omg|wow|woah|whoa|insane|crazy|unbelievable|incredible|amazing)\b',
            # Laughter
            r'\b(haha|hahaha|lol|lmao|laughing)\b',
            # Reactions
            r'\b(no way|are you kidding|what the|holy|dude|bro)\b',
            # Achievement
            r'\b(finally|yes|got it|got him|nice|epic|legendary|rare)\b',
            # Surprise
            r'\b(wait|hold on|look at|check this|did you see)\b',
        ]
        
        moments = []
        
        for segment in segments:
            text = segment['text'].lower()
            timestamp = segment['start']
            
            score = 0
            reasons = []
            
            # Check for exciting keywords
            for pattern in exciting_keywords:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 2
                    reasons.append("exciting commentary")
                    break
            
            # Check for all caps (shouting)
            if any(word.isupper() and len(word) > 3 for word in segment['text'].split()):
                score += 1
                reasons.append("shouting")
            
            # Check for multiple exclamation marks
            if '!!' in segment['text'] or segment['text'].count('!') >= 2:
                score += 1
                reasons.append("excitement")
            
            if score > 0:
                moments.append({
                    'timestamp': timestamp,
                    'score': score,
                    'text': segment['text'],
                    'reasons': reasons
                })
        
        return moments
    
    def _analyze_motion_at_times(self, video_path, speech_moments):
        """Analyze motion intensity around speech moments"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        motion_scores = {}
        
        for moment in speech_moments:
            timestamp = moment['timestamp']
            frame_num = int(timestamp * fps)
            
            # Get 3 frames around this moment
            motion_score = 0
            for offset in [-30, 0, 30]:
                cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_num + offset))
                ret1, frame1 = cap.read()
                ret2, frame2 = cap.read()
                
                if ret1 and ret2:
                    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                    diff = cv2.absdiff(gray1, gray2)
                    motion_score += np.mean(diff)
            
            motion_scores[timestamp] = motion_score / 3
        
        cap.release()
        return motion_scores
    
    def _rank_moments(self, speech_moments, motion_scores):
        """Combine speech and motion scores to rank moments"""
        ranked = []
        
        for moment in speech_moments:
            timestamp = moment['timestamp']
            speech_score = moment['score']
            motion_score = motion_scores.get(timestamp, 0) / 10  # Normalize
            
            # Combined score
            total_score = (speech_score * 3) + motion_score  # Weight speech more
            
            reason = f"{', '.join(moment['reasons'])} - \"{moment['text'][:50]}\""
            
            ranked.append({
                'timestamp': timestamp,
                'engagement_score': min(10, int(total_score)),
                'reason': reason
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Space out moments (at least 30 seconds apart)
        spaced_moments = []
        for moment in ranked:
            if not spaced_moments or all(abs(moment['timestamp'] - m['timestamp']) > 30 for m in spaced_moments):
                spaced_moments.append(moment)
        
        return spaced_moments
