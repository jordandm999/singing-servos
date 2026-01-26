# Python Version Requirements

## Required: Python 3.10

**Spleeter** requires TensorFlow 2.12.1, which only works with **Python 3.10** on ARM Macs (M1/M2/M3).

If you have Python 3.11+ or an Intel Mac, you may need Python 3.10 for the best compatibility.

## Solution: Install Python 3.10

### Mac (Homebrew)

```bash
# Install Python 3.10
brew install python@3.10

# Verify installation
python3.10 --version
# Should show: Python 3.10.x
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv
```

### Windows

Download Python 3.10 from [python.org](https://www.python.org/downloads/) and install it alongside your current Python.

## Create Virtual Environment with Python 3.10

```bash
cd /Users/jordanmorgan/src/github.com/singing-servos

# Remove old venv if it exists
rm -rf .venv venv

# Create venv with Python 3.10
python3.10 -m venv .venv

# Activate it
source .venv/bin/activate

# Verify you're using Python 3.10
python --version
# Should show: Python 3.10.x

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Why This Happens

Spleeter requires TensorFlow 2.12.1, which has strict Python version requirements:
- **ARM Macs (M1/M2/M3)**: TensorFlow 2.12.1 only works with Python 3.10
- **Intel Macs/Linux**: More flexible, but Python 3.10 is safest

TensorFlow hasn't maintained backward compatibility well across Python versions.

## Alternative: Use Demucs (Python 3.13 Compatible)

If you prefer to use Python 3.13, we can switch to **Demucs** instead of Spleeter. Demucs is more actively maintained and supports newer Python versions.

However, Demucs:
- Is slower than Spleeter
- Uses more RAM
- Might not work well on Raspberry Pi Zero

For now, **stick with Python 3.11** for the best experience.

## On Raspberry Pi

Raspberry Pi OS typically comes with Python 3.9 or 3.11, so this won't be an issue there.
