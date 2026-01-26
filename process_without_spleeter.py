#!/usr/bin/env python3
"""
Process songs without Spleeter - for ARM Macs

Use this if you've already separated vocals using an online tool.

Usage:
    python3 process_without_spleeter.py songs/my_song.mp3 path/to/vocals.wav
"""
import sys
import shutil
from pathlib import Path

from config import Config
from audio_processor import AudioProcessor


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 process_without_spleeter.py <original_song.mp3> <vocals.wav>")
        print()
        print("Example:")
        print("  python3 process_without_spleeter.py songs/my_song.mp3 ~/Downloads/vocals.wav")
        print()
        print("First, separate vocals using:")
        print("  - https://vocalremover.org")
        print("  - https://www.lalal.ai")
        sys.exit(1)

    original_file = Path(sys.argv[1])
    vocals_file = Path(sys.argv[2])

    if not original_file.exists():
        print(f"Error: Original file not found: {original_file}")
        sys.exit(1)

    if not vocals_file.exists():
        print(f"Error: Vocals file not found: {vocals_file}")
        sys.exit(1)

    song_name = original_file.stem

    print(f"\n=== Processing {song_name} (without Spleeter) ===\n")

    # Load config
    config = Config()

    # Copy vocals to expected location
    vocals_dir = Path(config.paths['vocals_dir']) / song_name
    vocals_dir.mkdir(parents=True, exist_ok=True)

    target_vocals = vocals_dir / 'vocals.wav'
    if not target_vocals.exists():
        print(f"Copying vocals to {target_vocals}...")
        shutil.copy(vocals_file, target_vocals)

    # Create processor (without Spleeter)
    processor = AudioProcessor(config)

    # Analyze vocals and generate servo data
    print("Analyzing vocals...")
    times, amplitude, duration = processor.analyze_vocals(str(target_vocals))
    print(f"Duration: {duration:.2f} seconds")
    print(f"Analyzed {len(times)} frames")

    # Generate servo data for each servo
    print("\nGenerating servo data...")
    servo_data_map = {}

    for servo_config in config.servos:
        servo_data = processor.generate_servo_data(times, amplitude, servo_config.name)
        servo_data_map[servo_config.name] = servo_data

    # Save servo data
    output_dir = Path(config.paths['servo_data_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    for servo_name, data in servo_data_map.items():
        output_file = output_dir / f"{song_name}_{servo_name}.npy"
        import numpy as np
        np.save(output_file, data)
        print(f"Saved: {output_file}")

    print(f"\n✓ Processing complete!")
    print(f"\nTo play this song, run:")
    print(f"  python3 main.py play {song_name} --mock")


if __name__ == '__main__':
    main()
