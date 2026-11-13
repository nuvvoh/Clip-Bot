# Gaming Clip Bot

AI-powered system to automatically find, clip, and upload engaging gaming moments.

## Features
- 🎬 **Smart Video Analysis**: Uses Whisper AI to find exciting moments from speech
- ✂️ **Auto Clipping**: Creates high-quality 60-second clips
- 🎯 **Keyword Detection**: Finds "OH MY GOD!", "INSANE!", laughter, reactions
- 📤 **Multi-Platform Upload**: YouTube Shorts, Instagram Reels, Twitter (optional)

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Create clips from any gaming video
python3 main.py --url "YOUTUBE_VIDEO_URL" --ai whisper --game "GameName" --no-upload

# Check clips
open clips/
```

## Usage

**Basic:**
```bash
python3 main.py --url "VIDEO_URL" --ai whisper --game "Fortnite" --no-upload
```

**Fast (no speech analysis):**
```bash
python3 main.py --url "VIDEO_URL" --ai free --game "Minecraft" --no-upload
```

**With editing:**
```bash
python3 main.py --url "VIDEO_URL" --ai whisper --game "GTA" --edit "add text \"EPIC!\"" --no-upload
```

## Analysis Methods

- `--ai whisper`: Smart analysis (finds exciting speech + motion) - **Recommended**
- `--ai free`: Fast analysis (motion + scene changes only)

## Requirements
- Python 3.9+
- FFmpeg
- ~150MB for Whisper model (one-time download)

## Cost
100% FREE - runs locally, no API costs
