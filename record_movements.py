#!/usr/bin/env python3
"""
Interactive Movement Recorder

Record servo movements manually by pressing a key while the song plays.

Usage:
    python3 record_movements.py
"""
import sys
import time
import threading
import pygame
from pathlib import Path
from pynput import keyboard
from config import Config
from playback_engine import SongLibrary
import numpy as np


# CONFIGURATION
RECORD_KEY = keyboard.KeyCode.from_char('j')  # Key to press for mouth open
MIN_MOVEMENT_TIME = 0.15  # Seconds - minimum time between position changes (servo speed limit)

# Servo positions (binary: open or closed)
OPEN_POSITION = 60.0   # Degrees - mouth open
CLOSED_POSITION = 0.0  # Degrees - mouth closed


def filter_servo_data(servo_data: np.ndarray, min_time: float = MIN_MOVEMENT_TIME) -> np.ndarray:
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
    sample_rate = 50
    num_samples = len(times)
    new_positions = np.zeros(num_samples)

    # Fill in positions based on filtered keyframes
    filter_idx = 0
    for i, t in enumerate(times):
        # Advance to the appropriate filtered keyframe
        while filter_idx < len(filtered_times) - 1 and filtered_times[filter_idx + 1] <= t:
            filter_idx += 1
        new_positions[i] = filtered_positions[filter_idx]

    filtered_data = np.column_stack([times, new_positions])

    # Count movements before and after
    original_changes = np.sum(np.diff(positions) != 0)
    filtered_changes = np.sum(np.diff(new_positions) != 0)

    print(f"\nFiltering for servo speed (min {min_time*1000:.0f}ms between moves):")
    print(f"  Original movements: {original_changes}")
    print(f"  Filtered movements: {filtered_changes}")
    print(f"  Removed: {original_changes - filtered_changes} movements that were too fast")

    return filtered_data


class MovementRecorder:
    """Record servo movements in real-time while song plays."""

    def __init__(self, config):
        self.config = config
        self.recording = False
        self.key_events = []  # List of (timestamp, is_pressed) tuples
        self.start_time = None
        self.key_currently_pressed = False

    def on_press(self, key):
        """Called when a key is pressed."""
        if key == RECORD_KEY and self.recording and not self.key_currently_pressed:
            timestamp = time.time() - self.start_time
            self.key_events.append((timestamp, True))
            self.key_currently_pressed = True
            print(f"  ▶ OPEN @ {timestamp:.3f}s")

    def on_release(self, key):
        """Called when a key is released."""
        if key == RECORD_KEY and self.recording and self.key_currently_pressed:
            timestamp = time.time() - self.start_time
            self.key_events.append((timestamp, False))
            self.key_currently_pressed = False
            print(f"  ◼ CLOSE @ {timestamp:.3f}s")

        # ESC to stop recording early
        if key == keyboard.Key.esc:
            self.recording = False
            return False  # Stop listener

    def record(self, audio_file: str, duration: float):
        """
        Record movements while playing audio.

        Args:
            audio_file: Path to audio file
            duration: Duration of song in seconds
        """
        print("\n" + "=" * 60)
        print("RECORDING MOVEMENTS")
        print("=" * 60)
        print()
        print(f"Press 'J' key to open mouth")
        print(f"Release 'J' key to close mouth")
        print(f"Press ESC to stop recording early")
        print()

        # Countdown
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)

        print("\n🎵 RECORDING! Press 'J' in rhythm!\n")

        # Reset state
        self.key_events = []
        self.key_currently_pressed = False
        self.recording = True
        self.start_time = time.time()

        # Start keyboard listener in background
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

        # Play audio
        pygame.mixer.init(frequency=self.config.audio['sample_rate'])
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # Wait for song to finish or ESC pressed
        start = time.time()
        try:
            while pygame.mixer.music.get_busy() and self.recording:
                time.sleep(0.1)

                # Safety timeout
                if time.time() - start > duration + 5:
                    break

        except KeyboardInterrupt:
            print("\n\nRecording interrupted")

        # Stop everything
        pygame.mixer.music.stop()
        self.recording = False
        listener.stop()

        print("\n✓ Recording complete!")
        print(f"Recorded {len(self.key_events)} key events")

        return self.key_events

    def convert_to_servo_data(self, duration: float) -> np.ndarray:
        """
        Convert key events to servo position data.

        Args:
            duration: Total duration of song

        Returns:
            Array of (time, position) pairs where position is 0-1 (0°-90° range)
        """
        if not self.key_events:
            print("Warning: No key events recorded!")
            # Return all closed
            return np.array([[0.0, 0.0], [duration, 0.0]])

        print("\nConverting to servo movements...")

        # Sort events by time
        events = sorted(self.key_events, key=lambda x: x[0])

        # Build servo timeline
        # Sample at 50 Hz (every 0.02 seconds) for smooth playback
        sample_rate = 50
        num_samples = int(duration * sample_rate)
        times = np.linspace(0, duration, num_samples)
        positions = np.zeros(num_samples)

        # Process key events
        press_times = []
        release_times = []

        for timestamp, is_pressed in events:
            if is_pressed:
                press_times.append(timestamp)
            else:
                release_times.append(timestamp)

        # Build position array
        current_press_idx = 0
        current_release_idx = 0

        for i, t in enumerate(times):
            # Find current state
            is_pressed = False

            # Check if we're between a press and release
            for j, press_time in enumerate(press_times):
                if press_time <= t:
                    # Check if there's a corresponding release
                    if j < len(release_times):
                        if t < release_times[j]:
                            is_pressed = True
                            break
                    else:
                        # No release yet, still pressed
                        is_pressed = True
                        break

            if is_pressed:
                # Key is pressed - open
                positions[i] = 1.0  # Maps to 60°
            else:
                # Key is not pressed - closed
                positions[i] = 0.0  # Maps to 0°

        # Combine into servo data format
        servo_data = np.column_stack([times, positions])

        # Print statistics before filtering
        open_time = np.sum(positions == 1.0) / len(positions) * duration
        closed_time = np.sum(positions == 0.0) / len(positions) * duration

        print(f"\nMovement breakdown (before filtering):")
        print(f"  Open (60°):   {open_time:.2f}s ({open_time/duration*100:.1f}%)")
        print(f"  Closed (0°):  {closed_time:.2f}s ({closed_time/duration*100:.1f}%)")

        # Filter for servo speed limitations
        servo_data = filter_servo_data(servo_data)

        # Print statistics after filtering
        filtered_positions = servo_data[:, 1]
        open_time = np.sum(filtered_positions == 1.0) / len(filtered_positions) * duration
        closed_time = np.sum(filtered_positions == 0.0) / len(filtered_positions) * duration

        print(f"\nMovement breakdown (after filtering):")
        print(f"  Open (60°):   {open_time:.2f}s ({open_time/duration*100:.1f}%)")
        print(f"  Closed (0°):  {closed_time:.2f}s ({closed_time/duration*100:.1f}%)")

        return servo_data


def get_song_duration(audio_file: str) -> float:
    """Get duration of audio file."""
    import librosa
    y, sr = librosa.load(audio_file, sr=None)
    return librosa.get_duration(y=y, sr=sr)


def main():
    """Interactive recording interface."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MOVEMENT RECORDER")
    print("=" * 60)
    print()
    print("Record servo movements by pressing 'J' key while the song plays.")
    print()

    # Load config and library
    config = Config()
    library = SongLibrary(config)

    # List available songs
    library.list_songs()

    if not library.songs:
        print("\nNo songs available!")
        print("Add MP3 files to the songs/ directory first.")
        return 1

    # Select song
    print("\nEnter song name:")
    song_name = input("> ").strip()

    if not library.has_song(song_name):
        print(f"Error: Song '{song_name}' not found")
        return 1

    audio_file = library.get_song_path(song_name)
    if not audio_file:
        print(f"Error: Could not find audio file for '{song_name}'")
        return 1

    # Get song duration
    print("\nAnalyzing song...")
    duration = get_song_duration(audio_file)
    print(f"Duration: {duration:.2f} seconds")

    # Select recording mode
    print("\nSelect servos to record (comma-separated):")
    print("  Examples:")
    print("    1       - servo1 only")
    print("    2,3     - servo2 and servo3")
    print("    1,2,3   - all servos")
    print("    all     - all servos")

    mode = input("> ").strip().lower()

    servo_names = []
    if mode == 'all':
        servo_names = ['servo1', 'servo2', 'servo3']
    else:
        # Parse comma-separated numbers
        for part in mode.split(','):
            part = part.strip()
            if part == '1':
                servo_names.append('servo1')
            elif part == '2':
                servo_names.append('servo2')
            elif part == '3':
                servo_names.append('servo3')

    # Remove duplicates while preserving order
    servo_names = list(dict.fromkeys(servo_names))

    if not servo_names:
        print("Invalid selection. Please enter 1, 2, 3, or combinations like '2,3'")
        return 1

    print(f"\nWill record for: {', '.join(servo_names)}")

    # Record movements
    recorder = MovementRecorder(config)
    key_events = recorder.record(audio_file, duration)

    if not key_events:
        print("\nNo movements recorded. Exiting.")
        return 1

    # Convert to servo data
    servo_data = recorder.convert_to_servo_data(duration)

    # Save servo data for selected servos
    output_dir = Path(config.paths['servo_data_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving servo data...")
    for servo_name in servo_names:
        output_file = output_dir / f"{song_name}_{servo_name}.npy"
        np.save(output_file, servo_data)
        print(f"  Saved: {output_file}")

    print("\n" + "=" * 60)
    print("✓ RECORDING COMPLETE!")
    print("=" * 60)
    print(f"\nTo play back your recording:")
    print(f"  python3 main.py play {song_name} --mock")
    print()
    print(f"Settings used:")
    print(f"  Min movement time: {MIN_MOVEMENT_TIME*1000:.0f}ms")
    print(f"  Open position: {OPEN_POSITION}°")
    print(f"  Closed position: {CLOSED_POSITION}°")
    print("=" * 60 + "\n")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(1)
