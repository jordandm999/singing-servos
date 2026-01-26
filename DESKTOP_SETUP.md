# Desktop Setup Guide

Use this guide to set up and test the project on your Mac/PC before buying hardware.

## Prerequisites

- Python 3.8 or higher
- FFmpeg

### Install FFmpeg

**Mac (Homebrew):**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Setup Steps

### 1. Create Virtual Environment

```bash
cd /Users/jordanmorgan/src/github.com/singing-servos

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# On Windows: venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Spleeter (AI vocal separation)
- Librosa (audio analysis)
- Pygame (audio playback)
- NumPy, SciPy (math/signal processing)
- PyYAML (configuration)

**Note:** This might take a few minutes. Spleeter will download ~200MB of AI models on first use.

### 3. Verify Setup

```bash
python3 verify_setup.py
```

Look for green checkmarks ✓. If you see any red ✗, check the error messages.

## Usage (Desktop Mode)

### Test Servos in Mock Mode

```bash
python3 main.py test --mock
```

You'll see simulated servo movements printed to console.

### Process a Song

```bash
# Add a song
cp ~/Music/your_song.mp3 songs/

# Process it (this works without any hardware!)
python3 main.py process songs/your_song.mp3
```

**First time only:** Spleeter downloads AI models (~200MB)

**What you get:**
- `processed/vocals/your_song/vocals.wav` - Separated vocals
- `processed/servo_data/your_song_servo1.npy` - Servo movement data
- Similar files for servo2 and servo3

### Simulate Playback

```bash
python3 main.py play your_song --mock
```

- Audio plays through your speakers
- Console shows what servos would be doing
- Example: `[servo1] position: 0.82 (angle: 73.8°)`

### Interactive Mode

```bash
python3 main.py interactive --mock
```

Browse and play processed songs.

## What Works on Desktop

✅ Song processing (vocal separation & analysis)
✅ Servo simulation (see what they'd do)
✅ Audio playback
✅ Configuration and testing
✅ All development work

❌ Actual servo control (needs Raspberry Pi + hardware)

## Workflow: Desktop → Raspberry Pi

1. **Process songs on desktop** (faster!)
   ```bash
   python3 main.py process songs/*.mp3
   ```

2. **Copy to Raspberry Pi**
   ```bash
   # Compress processed data
   tar -czf processed.tar.gz processed/

   # Transfer to Pi
   scp processed.tar.gz pi@raspberrypi.local:~/singing-servos/
   scp songs/*.mp3 pi@raspberrypi.local:~/singing-servos/songs/

   # On Pi: extract
   tar -xzf processed.tar.gz
   ```

3. **Play on Pi** (with real servos!)
   ```bash
   # On the Pi (no --mock flag)
   python3 main.py play your_song
   ```

## Tips

- **Keep venv activated** while working: `source venv/bin/activate`
- **Process multiple songs** at once: `python3 main.py process songs/*.mp3`
- **Check what's processed**: `ls processed/servo_data/`
- **Test without sound**: Comment out `engine.play()` if needed

## Deactivating Virtual Environment

When done:
```bash
deactivate
```

## Next Time You Work

```bash
cd /Users/jordanmorgan/src/github.com/singing-servos
source venv/bin/activate
# ... work on project ...
deactivate
```

## Troubleshooting

**"command not found: python3"**
- Try `python` instead of `python3`
- Or install Python 3: `brew install python3`

**"No module named 'yaml'"**
- Make sure venv is activated: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**"FFmpeg not found"**
- Mac: `brew install ffmpeg`
- Check: `which ffmpeg`

**Spleeter is slow**
- Normal on first run (downloading models)
- Processing a 3-min song takes 1-5 minutes on a decent computer

**Import errors**
- Ensure venv is activated (you should see `(venv)` in prompt)
- Try: `pip install --upgrade -r requirements.txt`
