from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from pathlib import Path
import config

class VideoClipper:
    def __init__(self, output_dir='clips'):
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)
    
    def create_clips(self, video_path, moments, duration=60):
        """Create clips from identified moments"""
        clips_created = []
        video = VideoFileClip(video_path)
        
        for i, moment in enumerate(moments):
            timestamp = moment.get('timestamp', 0)
            reason = moment.get('reason', 'Engaging moment')
            
            start_time = max(0, timestamp - duration/2)
            end_time = min(video.duration, timestamp + duration/2)
            
            if end_time - start_time < config.MIN_CLIP_DURATION:
                continue
            
            clip = video.subclip(start_time, end_time)
            
            # Convert to Shorts format (9:16 vertical)
            clip = self._convert_to_shorts_format(clip)
            
            output_path = f"{self.output_dir}/clip_{i+1}_{int(timestamp)}.mp4"
            
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                bitrate='15000k',
                audio_bitrate='320k',
                fps=60,
                preset='veryslow',
                ffmpeg_params=['-crf', '15', '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p'],
                logger=None
            )
            
            clips_created.append({
                'path': output_path,
                'reason': reason,
                'timestamp': timestamp,
                'duration': end_time - start_time
            })
        
        video.close()
        return clips_created
    
    def _convert_to_shorts_format(self, clip):
        """Convert clip to YouTube Shorts format (9:16, 1080x1920)"""
        target_width = 1080
        target_height = 1920
        target_ratio = target_height / target_width  # 16:9 = 1.777
        
        # Get current dimensions
        current_width, current_height = clip.size
        current_ratio = current_height / current_width
        
        if current_ratio < target_ratio:
            # Video is too wide (horizontal) - crop sides
            new_width = int(current_height / target_ratio)
            x_center = current_width / 2
            x1 = int(x_center - new_width / 2)
            x2 = int(x_center + new_width / 2)
            clip = clip.crop(x1=x1, x2=x2)
        else:
            # Video is too tall or already vertical - crop top/bottom
            new_height = int(current_width * target_ratio)
            y_center = current_height / 2
            y1 = int(y_center - new_height / 2)
            y2 = int(y_center + new_height / 2)
            clip = clip.crop(y1=y1, y2=y2)
        
        # Resize to exact Shorts dimensions
        clip = clip.resize((target_width, target_height))
        
        return clip
    
    def edit_with_prompt(self, clip_path, edit_prompt):
        """Edit clip based on natural language prompt"""
        clip = VideoFileClip(clip_path)
        
        if 'speed up' in edit_prompt.lower():
            speed = self._extract_speed(edit_prompt)
            clip = clip.fx(lambda c: c.speedx(speed))
        
        if 'add text' in edit_prompt.lower():
            text = self._extract_text(edit_prompt)
            txt_clip = TextClip(text, fontsize=70, color='white', stroke_color='black', stroke_width=2)
            txt_clip = txt_clip.set_position('center').set_duration(3)
            clip = CompositeVideoClip([clip, txt_clip])
        
        if 'zoom' in edit_prompt.lower():
            clip = clip.resize(1.2)
        
        output_path = clip_path.replace('.mp4', '_edited.mp4')
        clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            bitrate='15000k',
            audio_bitrate='320k',
            fps=60,
            preset='veryslow',
            ffmpeg_params=['-crf', '15', '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p'],
            logger=None
        )
        clip.close()
        
        return output_path
    
    def _extract_speed(self, prompt):
        """Extract speed multiplier from prompt"""
        import re
        match = re.search(r'(\d+\.?\d*)x', prompt)
        return float(match.group(1)) if match else 1.5
    
    def _extract_text(self, prompt):
        """Extract text to add from prompt"""
        import re
        match = re.search(r'"([^"]*)"', prompt)
        return match.group(1) if match else 'GTA VI'
