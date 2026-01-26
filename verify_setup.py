#!/usr/bin/env python3
"""
Setup Verification Script

Run this on your desktop/laptop to verify everything works
before buying hardware or moving to Raspberry Pi.
"""
import sys
from pathlib import Path


def check_dependencies():
    """Check if all required Python packages are installed."""
    print("=" * 60)
    print("STEP 1: Checking Python Dependencies")
    print("=" * 60)

    required = {
        'numpy': 'numpy',
        'librosa': 'librosa',
        'spleeter': 'spleeter',
        'pygame': 'pygame',
        'yaml': 'pyyaml',
        'scipy': 'scipy',
    }

    optional = {
        'pigpio': 'pigpio (only needed on Raspberry Pi)',
    }

    all_good = True

    print("\nRequired packages:")
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            all_good = False

    print("\nOptional packages:")
    for module, package in optional.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ○ {package} - Not installed (OK for now)")

    return all_good


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("\n" + "=" * 60)
    print("STEP 2: Checking FFmpeg")
    print("=" * 60)

    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True,
                              timeout=5)
        if result.returncode == 0:
            print("  ✓ FFmpeg is installed")
            return True
        else:
            print("  ✗ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("  ✗ FFmpeg not found")
        print("\n  Install FFmpeg:")
        print("    Mac: brew install ffmpeg")
        print("    Linux: sudo apt install ffmpeg")
        print("    Windows: Download from ffmpeg.org")
        return False
    except Exception as e:
        print(f"  ? Could not check FFmpeg: {e}")
        return False


def test_audio_processing():
    """Test that we can import audio processing modules."""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Audio Processing")
    print("=" * 60)

    try:
        from audio_processor import AudioProcessor
        from config import Config

        config = Config()
        processor = AudioProcessor(config)

        print("  ✓ Audio processor initialized")

        if processor.separator:
            print("  ✓ Spleeter loaded successfully")
        else:
            print("  ⚠ Spleeter not initialized (might download models on first use)")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_servo_controller():
    """Test servo controller in mock mode."""
    print("\n" + "=" * 60)
    print("STEP 4: Testing Servo Controller (Mock Mode)")
    print("=" * 60)

    try:
        from servo_controller import ServoController
        from config import Config

        config = Config()
        controller = ServoController(config, mock_mode=True)

        print("  ✓ Servo controller initialized in mock mode")
        print(f"  ✓ Found {len(controller.servos)} servos in config")

        # Test setting a position
        controller.set_position('servo1', 0.5)
        print("  ✓ Can control servos (in mock mode)")

        controller.cleanup()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_playback_engine():
    """Test playback engine."""
    print("\n" + "=" * 60)
    print("STEP 5: Testing Playback Engine")
    print("=" * 60)

    try:
        from playback_engine import PlaybackEngine
        from servo_controller import ServoController
        from config import Config

        config = Config()
        controller = ServoController(config, mock_mode=True)
        engine = PlaybackEngine(config, controller)

        print("  ✓ Playback engine initialized")

        controller.cleanup()
        engine.cleanup()
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_directories():
    """Check project directory structure."""
    print("\n" + "=" * 60)
    print("STEP 6: Checking Directory Structure")
    print("=" * 60)

    dirs = ['songs', 'processed', 'processed/vocals', 'processed/servo_data', 'config']

    for dir_path in dirs:
        p = Path(dir_path)
        if p.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ○ {dir_path}/ - Creating...")
            p.mkdir(parents=True, exist_ok=True)

    return True


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("SINGING SERVOS - SETUP VERIFICATION")
    print("=" * 60)
    print("\nThis will verify your setup is ready to process songs.")
    print("No hardware required for this test!\n")

    results = []

    results.append(("Dependencies", check_dependencies()))
    results.append(("FFmpeg", check_ffmpeg()))
    results.append(("Directories", check_directories()))
    results.append(("Audio Processing", test_audio_processing()))
    results.append(("Servo Controller", test_servo_controller()))
    results.append(("Playback Engine", test_playback_engine()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("✓ ALL CHECKS PASSED!")
        print("\nYou're ready to process songs!")
        print("\nNext steps:")
        print("  1. Add an MP3 to the songs/ directory")
        print("  2. Run: python3 main.py process songs/your_song.mp3")
        print("  3. The processing will work on your computer")
        print("  4. Later, copy processed/ folder to your Raspberry Pi")
        print("\nNo hardware needed yet!")
    else:
        print("⚠ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before processing songs.")
        print("\nMost likely fix:")
        print("  pip3 install -r requirements.txt")

    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
