# ARM Mac Setup (M1/M2/M3)

## The Problem

Spleeter (the AI vocal separation library) requires TensorFlow 2.12.1, which **doesn't exist for ARM Macs**. Apple Silicon only has TensorFlow 2.13+.

This is a known issue with no easy fix.

## Solutions

### Option 1: Use Online Vocal Separation (Easiest)

Separate vocals manually using free online tools, then use this project for servo control:

1. **Install dependencies (without Spleeter)**
```bash
cd /Users/jordanmorgan/src/github.com/singing-servos
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements-no-spleeter.txt
```

2. **Separate vocals online**
   - Upload your MP3 to [vocalremover.org](https://vocalremover.org) (free)
   - Or [lalal.ai](https://www.lalal.ai) (3 free songs)
   - Download the "vocals" track as WAV

3. **Manually create the file structure**
```bash
# For a song called "my_song.mp3"
mkdir -p processed/vocals/my_song
# Place the vocals.wav file you downloaded into:
# processed/vocals/my_song/vocals.wav
```

4. **Process with our code** (skips Spleeter, does the rest)
```bash
python3 process_without_spleeter.py songs/my_song.mp3 processed/vocals/my_song/vocals.wav
```

Let me create that script for you...

### Option 2: Process on Raspberry Pi

Your Raspberry Pi (ARM Linux) CAN run Spleeter because TensorFlow is available for ARM Linux, just not ARM macOS.

1. Set up project on Pi
2. Process songs there (will be slow on Pi Zero)
3. Copy processed files back to Mac for development

### Option 3: Use Intel Mac or Linux

If you have access to an Intel Mac or Linux machine, Spleeter works fine there.

### Option 4: Docker (Advanced)

Run Spleeter in a Docker container with x86_64 emulation, but this is complex and slow.

## Recommended: Option 1

For now, use online tools for vocal separation. Everything else in the project works perfectly on ARM Macs!

You can:
- ✅ Test servos in mock mode
- ✅ Analyze vocals
- ✅ Generate servo data
- ✅ Test playback
- ✅ Develop and test code

Just can't do automatic vocal separation locally.
