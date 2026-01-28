#!/usr/bin/env python3
"""
Process Call and Response Songs

Allows you to assign different time ranges to different servos.

Usage:
    python3 process_call_and_response.py songs/my_son_john.mp3 processed/vocals/my_son_john/vocals.wav
"""
import sys
import numpy as np
from pathlib import Path
from config import Config
from audio_processor import AudioProcessor


def parse_time_ranges(ranges_str):
    """
    Parse time ranges like "0-10,15-20" into list of (start, end) tuples.

    Args:
        ranges_str: String like "0-10,15-20" or "0-10,15-20,25-30"

    Returns:
        List of (start, end) tuples in seconds
    """
    if not ranges_str or ranges_str.strip().lower() == 'all':
        return None

    ranges = []
    for part in ranges_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ranges.append((float(start), float(end)))

    return ranges if ranges else None


def apply_time_mask(times, amplitude, time_ranges):
    """
    Mask amplitude to only include specified time ranges.

    Args:
        times: Time array
        amplitude: Amplitude array
        time_ranges: List of (start, end) tuples, or None for all

    Returns:
        Masked amplitude array
    """
    if time_ranges is None:
        return amplitude

    # Create mask (all zeros)
    mask = np.zeros_like(amplitude)

    # Set to 1 for time ranges we want
    for start, end in time_ranges:
        mask[(times >= start) & (times <= end)] = 1.0

    # Apply mask
    return amplitude * mask


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 process_call_and_response.py <original_song.mp3> <vocals.wav>")
        print()
        print("This script lets you assign different parts of the song to different servos.")
        sys.exit(1)

    original_file = Path(sys.argv[1])
    vocals_file = Path(sys.argv[2])

    if not original_file.exists() or not vocals_file.exists():
        print("Error: File not found")
        sys.exit(1)

    song_name = original_file.stem
    config = Config()

    print("\n" + "=" * 60)
    print(f"CALL AND RESPONSE PROCESSING: {song_name}")
    print("=" * 60)
    print()
    print("This tool lets you assign time ranges to each servo.")
    print("For example, in 'My Son John':")
    print("  - Servo1 sings the 'call' (solo parts)")
    print("  - Servo2 & Servo3 sing the 'response' (chorus parts)")
    print()
    print("Time range format: start-end,start-end")
    print("Example: 0-5.5,10-15.2")
    print("Or type 'all' for the whole song")
    print()

    # Create processor
    processor = AudioProcessor(config)

    # Analyze vocals once
    print("Analyzing vocals...")
    times, amplitude, duration = processor.analyze_vocals(str(vocals_file))
    print(f"Song duration: {duration:.2f} seconds")
    print()

    # Get time ranges for each servo
    servo_ranges = {}

    for servo_config in config.servos:
        print(f"\n{servo_config.name}:")
        print(f"  Enter time ranges for {servo_config.name} to sing")
        print(f"  Format: start-end,start-end (e.g., '0-5.5,10-15.2')")
        print(f"  Or 'all' for entire song")
        print(f"  Or press Enter to skip this servo")

        ranges_input = input(f"  > ").strip()

        if ranges_input:
            time_ranges = parse_time_ranges(ranges_input)
            servo_ranges[servo_config.name] = time_ranges

            if time_ranges:
                print(f"  → {servo_config.name} will sing during:")
                for start, end in time_ranges:
                    print(f"      {start:.2f}s - {end:.2f}s")
            else:
                print(f"  → {servo_config.name} will sing the whole song")

    # Generate servo data with time masks
    print("\nGenerating servo data...")
    output_dir = Path(config.paths['servo_data_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    for servo_name, time_ranges in servo_ranges.items():
        # Apply time mask
        masked_amplitude = apply_time_mask(times, amplitude, time_ranges)

        # Generate servo data
        servo_data = processor.generate_servo_data(times, masked_amplitude, servo_name)

        # Save
        output_file = output_dir / f"{song_name}_{servo_name}.npy"
        np.save(output_file, servo_data)
        print(f"  Saved: {output_file}")

        # Calculate how much this servo sings
        active_time = np.sum(masked_amplitude > 0) / len(masked_amplitude) * duration
        print(f"    Active time: {active_time:.2f}s ({active_time/duration*100:.1f}%)")

    print("\n" + "=" * 60)
    print("✓ Processing complete!")
    print(f"\nTo play: python3 main.py play {song_name} --mock")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
