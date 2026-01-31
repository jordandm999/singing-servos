#!/usr/bin/env python3
"""
Filter Existing Servo Recordings

Processes existing .npy servo data files to remove movements that are
too fast for the servos to achieve.

Usage:
    python3 filter_movements.py                    # Filter all songs
    python3 filter_movements.py my_son_john        # Filter specific song
    python3 filter_movements.py --min-time 200     # Custom minimum time (ms)
"""
import sys
import argparse
from pathlib import Path
import numpy as np

from config import Config


# Default minimum time between movements (milliseconds)
DEFAULT_MIN_TIME_MS = 150


def filter_servo_data(servo_data: np.ndarray, min_time: float) -> np.ndarray:
    """
    Filter servo data to remove movements that are too fast for servos.

    Args:
        servo_data: Array of (time, position) pairs
        min_time: Minimum time between position changes in seconds

    Returns:
        Filtered array with achievable movements only
    """
    if len(servo_data) < 2:
        return servo_data

    times = servo_data[:, 0]
    positions = servo_data[:, 1]

    # Find where position actually changes
    filtered_times = [times[0]]
    filtered_positions = [positions[0]]
    last_change_time = times[0]
    last_position = positions[0]

    for i in range(1, len(times)):
        current_pos = positions[i]
        current_time = times[i]

        # Check if position changed
        if current_pos != last_position:
            # Check if enough time has passed since last change
            if current_time - last_change_time >= min_time:
                filtered_times.append(current_time)
                filtered_positions.append(current_pos)
                last_change_time = current_time
                last_position = current_pos
            # If not enough time, skip this movement (keep previous position)

    # Always include the final position
    if filtered_times[-1] != times[-1]:
        filtered_times.append(times[-1])
        filtered_positions.append(filtered_positions[-1])

    # Rebuild the full timeline at original sample rate
    num_samples = len(times)
    new_positions = np.zeros(num_samples)

    # Fill in positions based on filtered keyframes
    filter_idx = 0
    for i, t in enumerate(times):
        # Advance to the appropriate filtered keyframe
        while filter_idx < len(filtered_times) - 1 and filtered_times[filter_idx + 1] <= t:
            filter_idx += 1
        new_positions[i] = filtered_positions[filter_idx]

    return np.column_stack([times, new_positions])


def filter_song(song_name: str, servo_data_dir: Path, min_time_ms: float, backup: bool = True):
    """
    Filter all servo data files for a song.

    Args:
        song_name: Name of the song
        servo_data_dir: Directory containing servo data files
        min_time_ms: Minimum time between movements in milliseconds
        backup: Whether to create backup of original files
    """
    min_time = min_time_ms / 1000.0  # Convert to seconds

    print(f"\nProcessing: {song_name}")
    print(f"  Minimum movement time: {min_time_ms:.0f}ms")

    # Find all servo files for this song
    pattern = f"{song_name}_servo*.npy"
    files = list(servo_data_dir.glob(pattern))

    if not files:
        print(f"  No servo data files found matching '{pattern}'")
        return False

    for file_path in files:
        servo_name = file_path.stem.replace(f"{song_name}_", "")
        print(f"\n  {servo_name}:")

        # Load original data
        original_data = np.load(file_path)
        original_positions = original_data[:, 1]
        original_changes = np.sum(np.diff(original_positions) != 0)

        # Create backup
        if backup:
            backup_path = file_path.with_suffix('.npy.backup')
            if not backup_path.exists():
                np.save(backup_path, original_data)
                print(f"    Backup saved: {backup_path.name}")

        # Filter the data
        filtered_data = filter_servo_data(original_data, min_time)
        filtered_positions = filtered_data[:, 1]
        filtered_changes = np.sum(np.diff(filtered_positions) != 0)

        # Save filtered data
        np.save(file_path, filtered_data)

        # Report
        removed = original_changes - filtered_changes
        print(f"    Original movements: {original_changes}")
        print(f"    Filtered movements: {filtered_changes}")
        print(f"    Removed: {removed} ({removed/max(original_changes,1)*100:.1f}% reduction)")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Filter servo recordings to remove movements too fast for servos"
    )
    parser.add_argument(
        'song_name',
        nargs='?',
        help='Song name to filter (omit to filter all songs)'
    )
    parser.add_argument(
        '--min-time',
        type=float,
        default=DEFAULT_MIN_TIME_MS,
        help=f'Minimum time between movements in milliseconds (default: {DEFAULT_MIN_TIME_MS})'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup files'
    )
    parser.add_argument(
        '--restore',
        action='store_true',
        help='Restore from backup files instead of filtering'
    )

    args = parser.parse_args()

    # Load config
    config = Config()
    servo_data_dir = Path(config.paths['servo_data_dir'])

    if not servo_data_dir.exists():
        print(f"Error: Servo data directory not found: {servo_data_dir}")
        return 1

    print("=" * 60)
    print("SERVO MOVEMENT FILTER")
    print("=" * 60)

    # Handle restore mode
    if args.restore:
        print("\nRestoring from backups...")
        backup_files = list(servo_data_dir.glob("*.npy.backup"))
        if not backup_files:
            print("No backup files found.")
            return 1

        for backup_path in backup_files:
            original_path = backup_path.with_suffix('')  # Remove .backup
            if args.song_name and args.song_name not in backup_path.name:
                continue
            data = np.load(backup_path)
            np.save(original_path, data)
            print(f"  Restored: {original_path.name}")

        print("\nRestore complete!")
        return 0

    # Find songs to process
    if args.song_name:
        songs = [args.song_name]
    else:
        # Find all unique song names from servo data files
        files = list(servo_data_dir.glob("*_servo*.npy"))
        songs = set()
        for f in files:
            # Extract song name (everything before _servo)
            name = f.stem
            for servo in ['_servo1', '_servo2', '_servo3']:
                if servo in name:
                    name = name.replace(servo, '')
                    break
            songs.add(name)
        songs = sorted(songs)

    if not songs:
        print("\nNo servo data files found to filter.")
        return 1

    print(f"\nFound {len(songs)} song(s) to process")

    # Process each song
    success_count = 0
    for song_name in songs:
        if filter_song(song_name, servo_data_dir, args.min_time, backup=not args.no_backup):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"Filtered {success_count}/{len(songs)} songs")
    print("=" * 60)

    if not args.no_backup:
        print("\nBackups saved with .backup extension.")
        print("To restore originals: python3 filter_movements.py --restore")

    return 0


if __name__ == '__main__':
    sys.exit(main())
