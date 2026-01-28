# Hardware Setup Guide

Complete wiring guide for Raspberry Pi Zero 2 W with servos, speaker, and button.

## Parts List

- Raspberry Pi Zero 2 W
- 3x Servo motors (SG90 or similar)
- Momentary push button
- Speaker (3.5mm or USB)
- 5V power supply for servos (2A+ recommended)
- Jumper wires
- Breadboard (optional, but helpful)

## Pi Zero 2 W Pinout Reference

```
                    Pi Zero 2 W
                 ┌─────────────┐
          3.3V  1│ o       o │2  5V
   (SDA) GPIO 2 3│ o       o │4  5V
   (SCL) GPIO 3 5│ o       o │6  GND
  BUTTON GPIO 4 7│ o       o │8  GPIO 14 (TX)
            GND 9│ o       o │10 GPIO 15 (RX)
        GPIO 17 11│ o       o │12 GPIO 18 (PWM)
        GPIO 27 13│ o       o │14 GND
        GPIO 22 15│ o       o │16 GPIO 23
          3.3V 17│ o       o │18 GPIO 24
        GPIO 10 19│ o       o │20 GND
         GPIO 9 21│ o       o │22 GPIO 25
        GPIO 11 23│ o       o │24 GPIO 8
            GND 25│ o       o │26 GPIO 7
         GPIO 0 27│ o       o │28 GPIO 1
         GPIO 5 29│ o       o │30 GND
         GPIO 6 31│ o       o │32 GPIO 12
        GPIO 13 33│ o       o │34 GND
        GPIO 19 35│ o       o │36 GPIO 16
        GPIO 26 37│ o       o │38 GPIO 20
            GND 39│ o       o │40 GPIO 21
                 └─────────────┘
```

## Wiring Diagram

```
                                    EXTERNAL 5V POWER
                                    (for servos)
                                         │
                                         │ +5V
                                    ┌────┴────┐
                                    │         │
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │   RASPBERRY PI ZERO 2 W                                  │
    │                                                          │
    │   Pin 7 (GPIO 4) ────────────┐                          │
    │                              │                          │
    │   Pin 9 (GND) ───────────────┼──┐                       │
    │                              │  │                       │
    │   Pin 11 (GPIO 17) ──────────┼──┼───── Servo 1 Signal   │
    │                              │  │      (yellow/white)   │
    │   Pin 13 (GPIO 27) ──────────┼──┼───── Servo 2 Signal   │
    │                              │  │      (yellow/white)   │
    │   Pin 15 (GPIO 22) ──────────┼──┼───── Servo 3 Signal   │
    │                              │  │      (yellow/white)   │
    │                              │  │                       │
    │   3.5mm Audio Jack ──────────┼──┼───── Speaker          │
    │                              │  │                       │
    └──────────────────────────────┼──┼───────────────────────┘
                                   │  │
                              ┌────┘  │
                              │       │
                           [BUTTON]   │
                              │       │
                              └───────┴─── COMMON GROUND ───┬──┬──┬──┐
                                                            │  │  │  │
                                                     Servo1 │  │  │  │
                                                     GND    │  │  │  │
                                                   (brown)  │  │  │  │
                                                            │  │  │  │
                                                     Servo2 ┘  │  │  │
                                                     GND       │  │  │
                                                               │  │  │
                                                     Servo3 ───┘  │  │
                                                     GND          │  │
                                                                  │  │
                                              External PSU GND ───┘  │
                                                                     │
                                              Pi GND ────────────────┘
```

## Servo Wiring (IMPORTANT!)

### Servo Wire Colors
- **Brown/Black** = Ground (GND)
- **Red** = Power (+5V)
- **Yellow/Orange/White** = Signal

### Connections

| Servo   | Signal Wire → Pi | Power (+5V) | Ground |
|---------|------------------|-------------|--------|
| Servo 1 | GPIO 17 (pin 11) | External 5V | Common GND |
| Servo 2 | GPIO 27 (pin 13) | External 5V | Common GND |
| Servo 3 | GPIO 22 (pin 15) | External 5V | Common GND |

### ⚠️ CRITICAL: Servo Power

**DO NOT power servos from the Pi's 5V pin!**

Servos draw too much current and will:
- Cause the Pi to brown out and reboot
- Damage the Pi over time
- Cause erratic servo behavior

**Use an external 5V power supply:**
- 5V, 2A minimum (3A recommended for 3 servos)
- Connect external power GND to Pi GND (they MUST share ground)
- Connect external power +5V to servo red wires only

## Button Wiring

Simple 2-wire connection:

| Button Pin | Connects To |
|------------|-------------|
| Pin 1      | GPIO 4 (Pi pin 7) |
| Pin 2      | GND (Pi pin 9) |

The code uses an internal pull-up resistor, so no external resistor is needed.

**How it works:**
- Button not pressed: GPIO 4 reads HIGH (pulled up internally)
- Button pressed: GPIO 4 reads LOW (connected to ground)

## Speaker Options

### Option 1: 3.5mm Audio Jack (Easiest)

Just plug any powered speaker or headphones into the Pi's 3.5mm jack.

**Setup:**
```bash
# Set audio output to 3.5mm jack
sudo raspi-config
# Navigate to: System Options → Audio → Headphones
```

### Option 2: USB Speaker

Plug in a USB speaker. It should be detected automatically.

**Check it's detected:**
```bash
aplay -l
```

### Option 3: HDMI Audio

If using a monitor with speakers, audio can go through HDMI.

```bash
sudo raspi-config
# Navigate to: System Options → Audio → HDMI
```

### Option 4: I2S DAC (Best Quality)

For better audio quality, use an I2S DAC board like:
- Adafruit I2S 3W Stereo Speaker Bonnet
- pHAT DAC
- HiFiBerry

These require additional setup - see their documentation.

## Testing Audio

```bash
# Test with a simple sound
speaker-test -t wav -c 2

# Adjust volume
alsamixer
```

## Complete Setup Steps

### 1. Wire Everything Up

1. **Power off the Pi**
2. Connect servos (signal wires only) to GPIO 17, 27, 22
3. Connect button between GPIO 4 and GND
4. Connect speaker to 3.5mm jack
5. Connect external 5V power supply to servos
6. **Connect all grounds together** (Pi, servos, external power)

### 2. Software Setup on Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip pigpio python3-pigpio ffmpeg

# Start pigpio daemon
sudo pigpiod

# Enable pigpio on boot
sudo systemctl enable pigpiod

# Clone your repo
git clone https://github.com/jordandm999/singing-servos.git
cd singing-servos

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements-no-spleeter.txt

# Set audio output
sudo raspi-config
# System Options → Audio → Headphones (or your choice)
```

### 3. Copy Your Processed Songs

From your Mac, copy the processed data:

```bash
# On your Mac:
cd /Users/jordanmorgan/src/github.com/singing-servos

# Copy processed data to Pi
scp -r processed/ pi@raspberrypi.local:~/singing-servos/

# Copy your songs
scp songs/*.mp3 pi@raspberrypi.local:~/singing-servos/songs/
```

### 4. Test Everything

```bash
# On the Pi:
cd ~/singing-servos
source .venv/bin/activate

# Test servos
python3 main.py test

# Test playing a song
python3 main.py play my_son_john

# Test button trigger
python3 button_trigger.py
```

### 5. Run on Boot (Optional)

Create a systemd service to start automatically:

```bash
sudo nano /etc/systemd/system/singing-servos.service
```

Add:
```ini
[Unit]
Description=Singing Servos
After=network.target pigpiod.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/singing-servos
Environment=PATH=/home/pi/singing-servos/.venv/bin:$PATH
ExecStart=/home/pi/singing-servos/.venv/bin/python3 button_trigger.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable singing-servos
sudo systemctl start singing-servos

# Check status
sudo systemctl status singing-servos

# View logs
journalctl -u singing-servos -f
```

## Troubleshooting

### Servos don't move

1. Check pigpio daemon: `sudo pigpiod`
2. Check wiring (signal wires to correct GPIO pins)
3. Check external power supply is on
4. Check grounds are all connected
5. Test with: `python3 main.py test`

### No audio

1. Check speaker is powered/connected
2. Set audio output: `sudo raspi-config` → Audio
3. Test audio: `speaker-test -t wav -c 2`
4. Check volume: `alsamixer`

### Button doesn't work

1. Check wiring (GPIO 4 to button, button to GND)
2. Test GPIO:
   ```bash
   python3 -c "import pigpio; pi=pigpio.pi(); print(pi.read(4))"
   ```
   Should print 1 (not pressed) or 0 (pressed)

### Pi reboots when servos move

- Servos are drawing power from Pi - use external power!
- Check that external power supply has enough current (2A+)

## Wiring Checklist

Before powering on:

- [ ] Servo signal wires connected to GPIO 17, 27, 22
- [ ] Servo power wires connected to external 5V (NOT Pi)
- [ ] Servo ground wires connected to common ground
- [ ] External power supply ground connected to Pi ground
- [ ] Button connected between GPIO 4 and GND
- [ ] Speaker connected to 3.5mm jack (or USB)
- [ ] All connections secure

## Pin Summary

| Component | GPIO | Physical Pin | Notes |
|-----------|------|--------------|-------|
| Servo 1   | 17   | 11           | Signal only |
| Servo 2   | 27   | 13           | Signal only |
| Servo 3   | 22   | 15           | Signal only |
| Button    | 4    | 7            | To GND when pressed |
| Ground    | -    | 9, 14, 20, 25, 30, 34, 39 | Use any GND pin |

Happy singing! 🎵🤖
