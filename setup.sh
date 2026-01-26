#!/bin/bash
# Setup script for Singing Servos on Raspberry Pi

echo "=== Singing Servos Setup Script ==="
echo ""

# Check if running on Linux (Raspberry Pi)
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Warning: This script is designed for Raspberry Pi (Linux)"
    echo "You can still install Python dependencies, but GPIO features won't work."
    echo ""
fi

# Update system
echo "Step 1: Updating system packages..."
if command -v apt &> /dev/null; then
    sudo apt update
fi

# Install system dependencies
echo ""
echo "Step 2: Installing system dependencies..."
if command -v apt &> /dev/null; then
    sudo apt install -y python3-pip python3-dev libasound2-dev portaudio19-dev ffmpeg pigpio python3-pigpio
else
    echo "apt not found - skipping system dependencies"
    echo "Make sure you have: python3, pip, ffmpeg, pigpio"
fi

# Install Python dependencies
echo ""
echo "Step 3: Installing Python dependencies..."
pip3 install -r requirements.txt

# Start pigpio daemon (Raspberry Pi only)
if command -v pigpiod &> /dev/null; then
    echo ""
    echo "Step 4: Starting pigpio daemon..."
    sudo pigpiod

    # Enable pigpio to start on boot
    echo "Enabling pigpio to start on boot..."
    sudo systemctl enable pigpiod || echo "Could not enable pigpiod service"
else
    echo ""
    echo "Step 4: pigpio not found - skipping daemon start"
fi

# Create directories
echo ""
echo "Step 5: Creating directories..."
mkdir -p songs processed/vocals processed/servo_data config

# Generate default config
echo ""
echo "Step 6: Generating default configuration..."
python3 main.py config

# Make scripts executable
echo ""
echo "Step 7: Making scripts executable..."
chmod +x main.py examples/*.py setup.sh

# Test audio
echo ""
echo "Step 8: Testing audio output..."
if command -v speaker-test &> /dev/null; then
    echo "Run 'speaker-test -t wav -c 2' to test your speakers"
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "  1. Test servos: python3 main.py test"
echo "  2. Calibrate: python3 examples/calibrate_servos.py"
echo "  3. Add MP3 to songs/ directory"
echo "  4. Process: python3 main.py process songs/your_song.mp3"
echo "  5. Play: python3 main.py play your_song"
echo ""
echo "See README.md for detailed instructions!"
