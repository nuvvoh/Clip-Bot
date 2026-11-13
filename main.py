import argparse
from downloader import VideoDownloader
from free_analyzer import SimpleFreeAnalyzer
from whisper_analyzer import WhisperSmartAnalyzer
from clipper import VideoClipper
from uploader import MultiPlatformUploader
import config

def main():
    parser = argparse.ArgumentParser(description='Gaming Clip Bot - Auto clip and upload from any gaming video')
    parser.add_argument('--url', required=True, help='Video URL to process')
    parser.add_argument('--ai', default='whisper', choices=['free', 'whisper'], help='AI provider (whisper=smart, free=fast)')
    parser.add_argument('--duration', type=int, default=60, help='Clip duration in seconds')
    parser.add_argument('--no-upload', action='store_true', help='Skip uploading')
    parser.add_argument('--edit', help='Edit prompt (e.g., "add text \"EPIC!\" and speed up 2x")')
    parser.add_argument('--game', help='Game name for titles (e.g., "Fortnite", "Minecraft")')
    
    args = parser.parse_args()
    
    print("=== Gaming Clip Bot ===\n")
    
    print("1. Downloading video...")
    downloader = VideoDownloader()
    video_info = downloader.download(args.url)
    print(f"✓ Downloaded: {video_info['title']}")
    
    print("\n2. Analyzing video for engaging moments...")
    if args.ai == 'whisper':
        analyzer = WhisperSmartAnalyzer()
    else:
        analyzer = SimpleFreeAnalyzer()
    moments = analyzer.analyze_moments(video_info['filepath'])
    print(f"✓ Found {len(moments)} engaging moments")
    
    if not moments:
        print("No engaging moments found. Exiting.")
        downloader.cleanup(video_info['filepath'])
        return
    
    print("\n3. Creating clips...")
    clipper = VideoClipper()
    clips = clipper.create_clips(video_info['filepath'], moments, duration=args.duration)
    print(f"✓ Created {len(clips)} clips")
    
    if args.edit:
        print(f"\n4. Applying edits: {args.edit}")
        for clip in clips:
            clip['path'] = clipper.edit_with_prompt(clip['path'], args.edit)
        print("✓ Edits applied")
    
    if not args.no_upload:
        print("\n5. Uploading to platforms...")
        uploader = MultiPlatformUploader()
        
        for i, clip in enumerate(clips):
            game_name = args.game or "Gaming"
            title = f"{game_name} - {clip['reason'][:50]}"
            description = f"{clip['reason']}\n\nFrom: {video_info['title']}"
            
            print(f"\nClip {i+1}/{len(clips)}:")
            results = uploader.upload_all(clip['path'], title, description)
            
            print(f"\nResults for clip {i+1}:")
            for platform, url in results.items():
                if url:
                    print(f"  {platform}: {url}")
    
    print("\n6. Cleaning up...")
    downloader.cleanup(video_info['filepath'])
    print("✓ Done!")

if __name__ == '__main__':
    main()
