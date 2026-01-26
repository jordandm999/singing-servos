# Singing Servos

Make your robots sing! This project uses a Raspberry Pi Zero 2 W to control servos connected to robot mouths, creating synchronized lip movements that match the vocals of any song.

## Features

- **Automatic Vocal Separation**: Extracts vocals from any MP3 using AI (Spleeter)
- **Natural Mouth Movements**: Servos move based on syllables and vocal amplitude, not just simple open/close
- **Multi-Servo Support**: Control up to 3 servos independently for different vocal parts
- **Call & Response**: Assign different vocal parts to different servos (e.g., lead vs backup)
- **Audio Playback**: Plays songs through a speaker connected to the Pi
- **Easy to Use**: Simple command-line interface for processing and playing songs

## Hardware Requirements

- Raspberry Pi Zero 2 W (or any Raspberry Pi with GPIO)
- 3x Servo motors (e.g., SG90, MG90S)
- Speaker (3.5mm jack or USB)
- Power supply for servos (5V, 2A+ recommended)
- Jumper wires
- (Optional) Breadboard for connections

## Hardware Setup

### Servo Connections

Default GPIO pin assignments (can be changed in config):

| Servo  | GPIO Pin | Physical Pin |
|--------|----------|--------------|
| Servo1 | GPIO 17  | Pin 11       |
| Servo2 | GPIO 27  | Pin 13       |
| Servo3 | GPIO 22  | Pin 15       |

**Important**: Servos need external power! Connect:
- Servo signal wires to GPIO pins (yellow/white wire)
- Servo ground to Pi GND (brown/black wire)
- Servo power (5V) to external power supply (red wire)
- Connect external power supply ground to Pi GND

### Audio Output

Connect a speaker to:
- 3.5mm headphone jack on the Pi, OR
- USB speaker, OR
- HDMI audio output

## Software Setup

### On Your Raspberry Pi

1. **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install System Dependencies**
```bash
# Audio libraries
sudo apt install -y python3-pip python3-dev libasound2-dev portaudio19-dev

# FFmpeg (required for audio processing)
sudo apt install -y ffmpeg

# pigpio daemon for servo control
sudo apt install -y pigpio python3-pigpio
```

3. **Start pigpio daemon**
```bash
sudo pigpiod
```

To start pigpio automatically on boot:
```bash
sudo systemctl enable pigpiod
```

4. **Clone This Repository**
```bash
git clone https://github.com/yourusername/singing-servos.git
cd singing-servos
```

5. **Install Python Dependencies**
```bash
pip3 install -r requirements.txt
```

**Note**: Spleeter will download ~200MB of AI models on first use. This may take a while on a Pi Zero.

### Alternative: Pre-process on Desktop

For faster processing, you can separate vocals on your desktop computer and transfer files to the Pi:

1. Install on desktop: `pip install -r requirements.txt`
2. Process songs: `python main.py process song.mp3`
3. Transfer files to Pi:
   - Copy `processed/` directory to Pi
   - Copy original MP3s to `songs/` directory on Pi

## Quick Start

### 1. Test Your Servos

Make sure everything is connected correctly:

```bash
python3 main.py test
```

This will move each servo through a test pattern. If you're not on a Pi yet, add `--mock` to simulate:

```bash
python3 main.py test --mock
```

### 2. Process a Song

Place your MP3 file in the `songs/` directory:

```bash
cp ~/my_song.mp3 songs/
```

Process it to extract vocals and generate servo movements:

```bash
python3 main.py process songs/my_song.mp3
```

This will:
- Separate vocals from the music
- Analyze the vocals for syllables and amplitude
- Generate servo movement data
- Save everything in `processed/`

**First run will be slow** as Spleeter downloads AI models (~200MB).

### 3. Play the Song

Once processed, play it back:

```bash
python3 main.py play my_song
```

Your robots will now sing along!

### 4. Interactive Mode

Browse and play your song library:

```bash
python3 main.py interactive
```

## Advanced Usage

### Custom Configuration

Generate a config file to customize servo pins and parameters:

```bash
python3 main.py config
```

This creates `config/default_config.yaml`. Edit it to change:

- GPIO pins for each servo
- Servo angle ranges (min/max mouth opening)
- Vocal detection sensitivity
- Smoothing parameters

Use your custom config:

```bash
python3 main.py --config config/my_config.yaml play my_song
```

### Servo Assignments (Call & Response)

Assign different vocal parts to different servos. For example, in a duet:

```bash
python3 main.py process songs/duet.mp3 \
  --servo-assignments '{"lead": ["servo1"], "backup": ["servo2", "servo3"]}'
```

This uses pitch-based separation to assign:
- High-pitched vocals → servo1
- Lower-pitched vocals → servo2 and servo3

**Note**: This is experimental and works best with songs that have distinct vocal ranges.

### All Servos Together (Default)

By default, all servos move together:

```bash
python3 main.py process songs/song.mp3 --all-servos
```

## Project Structure

```
singing-servos/
├── main.py                  # Main entry point
├── config.py                # Configuration management
├── audio_processor.py       # Vocal separation & analysis
├── servo_controller.py      # Servo control via GPIO
├── playback_engine.py       # Audio/servo synchronization
├── requirements.txt         # Python dependencies
├── songs/                   # Your MP3 files
├── processed/
│   ├── vocals/             # Separated vocal tracks
│   └── servo_data/         # Pre-processed servo movements
├── config/
│   └── default_config.yaml # Configuration file
└── examples/               # Example scripts
```

## How It Works

### 1. Vocal Separation (Spleeter)

Uses AI to separate vocals from the instrumental track:
- Input: `song.mp3`
- Output: `vocals.wav` + `accompaniment.wav`

### 2. Vocal Analysis (Librosa)

Analyzes the vocal track to extract:
- **Amplitude envelope**: How loud the vocals are over time
- **Syllable detection**: When the singer starts/stops singing
- **Pitch information**: For separating different voices

### 3. Servo Data Generation

Converts vocal features into servo positions:
- High amplitude = mouth open
- Low/no amplitude = mouth closed
- Smoothing applied for natural movement
- Mapped to 0-1 range (0=closed, 1=fully open)

### 4. Synchronized Playback

- Plays original song through speaker
- Updates servo positions in real-time (~100 Hz)
- Keeps audio and servos synchronized using timestamps

## Troubleshooting

### Servos Don't Move

1. Check pigpio daemon is running: `sudo pigpiod`
2. Verify GPIO pins in config match your wiring
3. Ensure servos have external power supply
4. Test servos: `python3 main.py test`

### No Audio Output

1. Check speaker connection
2. Test audio: `speaker-test -t wav -c 2`
3. Select audio output: `sudo raspi-config` → Advanced → Audio
4. Check volume: `alsamixer`

### Processing Too Slow

- Pre-process on desktop computer (see setup section)
- Use smaller audio files
- Consider using a faster Pi (Pi 4 recommended)

### Import Errors

```bash
# Reinstall dependencies
pip3 install --upgrade -r requirements.txt

# If pigpio errors:
sudo apt install -y pigpio python3-pigpio
```

### "pigpio not connected"

```bash
# Start the daemon
sudo pigpiod

# Check it's running
pgrep pigpiod
```

## Tips & Best Practices

1. **Start Simple**: Test with one servo before adding more
2. **Calibrate Servos**: Adjust `open_angle` and `closed_angle` in config for your robot mouths
3. **Power Supply**: Don't power servos from Pi's 5V pin - use external supply
4. **Song Choice**: Clear vocals work best (avoid heavy instrumental sections)
5. **Smoothing**: Increase `smoothing_window` in config for gentler movements
6. **Sensitivity**: Adjust `syllable_threshold` if servos are too sensitive/not sensitive enough

## Future Enhancements

Possible improvements:
- Web interface for song management
- Better vocal part separation (using Demucs or manual track editing)
- LED integration for eyes/effects
- Multiple song playlists
- Adjustable servo speed/acceleration curves

## Contributing

Contributions welcome! Ideas:
- Better vocal separation algorithms
- Support for more servos
- Real-time audio input (microphone karaoke mode)
- Dance move generation for additional servos

## License

MIT License - see LICENSE file

## Credits

- Built for Raspberry Pi robots that love to sing!
- Uses [Spleeter](https://github.com/deezer/spleeter) for vocal separation
- Uses [Librosa](https://librosa.org/) for audio analysis
- Uses [pigpio](http://abyz.me.uk/rpi/pigpio/) for servo control

## Support

Having issues? Check:
1. This README
2. Example configurations in `examples/`
3. Open an issue on GitHub

Happy singing!
