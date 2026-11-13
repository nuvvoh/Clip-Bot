import yt_dlp
import os
from pathlib import Path

class VideoDownloader:
    def __init__(self, output_dir='temp'):
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)
    
    def download(self, url):
        """Download video from URL and return local path"""
        # Check if it's a local file path
        if not url.startswith('http') and os.path.exists(url):
            return {
                'filepath': url,
                'title': os.path.basename(url),
                'duration': 0,
                'video_id': 'local'
            }
        
        # Also check absolute path
        abs_path = os.path.abspath(url)
        if os.path.exists(abs_path):
            return {
                'filepath': abs_path,
                'title': os.path.basename(abs_path),
                'duration': 0,
                'video_id': 'local'
            }
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': f'{self.output_dir}/%(id)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
            'extractor_args': {'youtube': {'player_client': ['android']}},
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            ext = info['ext']
            filepath = f"{self.output_dir}/{video_id}.{ext}"
            
            return {
                'filepath': filepath,
                'title': info.get('title', ''),
                'duration': info.get('duration', 0),
                'video_id': video_id
            }
    
    def cleanup(self, filepath):
        """Remove downloaded video"""
        if os.path.exists(filepath):
            os.remove(filepath)
