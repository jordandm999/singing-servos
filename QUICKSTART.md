# Quick Start Guide

Get your singing servos up and running in 5 minutes!

## Prerequisites

- Raspberry Pi Zero 2 W (or any Pi) with Raspbian OS
- 3 servos connected to GPIO pins (default: GPIO 17, 27, 22)
- External 5V power for servos
- Speaker connected to Pi

## Installation

### On Desktop (Mac/Linux/Windows)

1. **Clone and setup virtual environment**
```bash
git clone <your-repo-url> singing-servos
cd singing-servos

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### On Raspberry Pi

1. **Clone and setup**
```bash
git clone <your-repo-url> singing-servos
cd singing-servos
chmod +x setup.sh
./setup.sh
```

The setup script will install everything needed.

2. **Verify pigpio is running**
```bash
pgrep pigpiod
```

If nothing appears:
```bash
sudo pigpiod
```

## First Run

### Test Servos

Make sure everything works:

```bash
python3 main.py test
```

Each servo should move in a wave pattern. If not, check your connections!

### Process Your First Song

1. Copy an MP3 to the songs folder:
```bash
cp ~/music/my_favorite_song.mp3 songs/
```

2. Process it (this may take a few minutes):
```bash
python3 main.py process songs/my_favorite_song.mp3
```

3. Play it:
```bash
python3 main.py play my_favorite_song
```

Watch your robots sing!

## Interactive Mode

Browse and play songs easily:

```bash
python3 main.py interactive
```

## Troubleshooting

**Servos don't move?**
- Check connections
- Verify external power supply
- Run: `sudo pigpiod`
- Check config: `cat config/default_config.yaml`

**No audio?**
- Run: `speaker-test -t wav -c 2`
- Check volume: `alsamixer`
- Select output: `sudo raspi-config` > Advanced > Audio

**Processing fails?**
- Make sure FFmpeg is installed: `which ffmpeg`
- Check free disk space: `df -h`
- Try on desktop first, then transfer files

**Still stuck?**
- Check README.md for detailed troubleshooting
- Verify all dependencies: `pip3 install -r requirements.txt`

## Next Steps

- Calibrate servos: `python3 examples/calibrate_servos.py`
- Manual control: `python3 examples/manual_control.py`
- Customize config: `config/default_config.yaml`
- Read full docs: `README.md`

Have fun!
