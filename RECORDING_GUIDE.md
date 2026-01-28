# Manual Movement Recording Guide

The best way to get perfect servo movements is to record them yourself!

## How It Works

1. **Select a song** from your library
2. **Choose which servo(s)** to record for
3. **3-2-1 countdown**, then the song plays
4. **Press and hold 'J' key** when you want the mouth(s) open
5. **Release 'J' key** when you want the mouth(s) closed
6. Your timing is recorded and converted to servo movements

## Servo Positions

The system uses three positions based on your key presses:

- **60° (Fully Open)**: While 'J' key is pressed/held
- **30° (Half Open)**: When closed, but next mouth opening is < 0.3 seconds away
- **0° (Closed)**: When closed and next opening is > 0.3 seconds away

The "half open" position gives a more natural resting state between quick syllables.

## Usage

### Install Required Package

```bash
pip install pynput
```

### Run the Recorder

```bash
python3 record_movements.py
```

### Interactive Prompts

1. **Select song**: Type the name of a song in your library
2. **Select mode**:
   - `1` = Record for servo1 only
   - `2` = Record for servo2 only
   - `3` = Record for servo3 only
   - `4` = Record for ALL servos (same movements)

### Recording

- After the 3-2-1 countdown, the song starts playing
- **Press 'J' key** = mouth opens
- **Hold 'J' key** = mouth stays open
- **Release 'J' key** = mouth closes
- **Press ESC** = stop recording early

### Tips for Good Recording

1. **Listen first**: Play the song a few times to learn it
2. **Practice dry**: Go through the motions without recording
3. **Be rhythmic**: Press on the beat/syllables
4. **Use holds**: Hold the 'J' key for sustained notes
5. **Don't overthink**: Small imperfections add character!

## Recording Call and Response Songs

For songs like "My Son John" with different parts:

### Method 1: Record Separately

```bash
# First recording - servo1 does the "call" (solo parts)
python3 record_movements.py
> my_son_john
> 1  (servo1)
# Press 'J' key only during SOLO parts

# Second recording - servo2 & servo3 do the "response" (chorus)
python3 record_movements.py
> my_son_john
> 2  (servo2)
# Press 'J' key only during CHORUS parts

# Third recording
python3 record_movements.py
> my_son_john
> 3  (servo3)
# Press 'J' key only during CHORUS parts
```

### Method 2: Record All Together First

```bash
# Record all servos singing together
python3 record_movements.py
> my_son_john
> 4  (all servos)

# Then re-record specific servos for their unique parts
python3 record_movements.py
> my_son_john
> 1  (just servo1 for solos)
```

## Adjusting Settings

Edit these values in `record_movements.py` to customize:

```python
WAIT_TIME = 0.3        # Seconds - threshold for half vs. closed position
OPEN_POSITION = 60.0   # Degrees - fully open mouth
HALF_POSITION = 30.0   # Degrees - half open mouth
CLOSED_POSITION = 0.0  # Degrees - closed mouth
```

**WAIT_TIME tips:**
- **Lower (0.2s)**: More "half-open" positions, smoother between quick syllables
- **Higher (0.5s)**: More "fully closed" positions, sharper mouth movements

## Playback

After recording:

```bash
# Test in mock mode
python3 main.py play my_son_john --mock

# Play on Raspberry Pi with real servos
python3 main.py play my_son_john
```

## Re-recording

To redo a recording, just run the recorder again. It will overwrite the previous recording for that servo.

## Troubleshooting

**"No module named 'pynput'"**
```bash
pip install pynput
```

**Audio doesn't play**
- Check volume
- Verify audio file exists: `ls songs/`

**Movements don't match my presses**
- Check WAIT_TIME setting
- Make sure you're pressing 'J' key, not other keys
- Try recording again - practice makes perfect!

**Servo movements too fast/slow**
- This shouldn't happen - movements are timestamped to the song
- Make sure you're playing the same song you recorded with

## Example Workflow

```bash
# 1. Add song to library
cp ~/Music/sea_shanty.mp3 songs/

# 2. Listen and plan your recording
# (play it a few times, note where the vocals are)

# 3. Record movements
python3 record_movements.py

# 4. Select song and mode
> sea_shanty
> 4  (all servos for now)

# 5. After countdown, press 'J' key in rhythm!

# 6. Test it
python3 main.py play sea_shanty --mock

# 7. If not perfect, record again!
python3 record_movements.py
```

## Benefits of Manual Recording

✅ **Perfect timing** - matches your musical interpretation
✅ **Artistic control** - emphasize specific syllables or beats
✅ **No algorithms** - what you record is what you get
✅ **Quick iterations** - re-record until it's perfect
✅ **Works on ARM Macs** - no AI dependencies needed

Happy recording! 🎵
