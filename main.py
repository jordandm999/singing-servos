#!/usr/bin/env python3
"""
Singing Servos - Main Entry Point

Control servos to make robots sing along with songs!

Usage:
    python main.py process <song.mp3>              - Process a song for playback
    python main.py play <song_name>                - Play a processed song
    python main.py interactive                     - Interactive playback mode
    python main.py test                            - Test all servos
    python main.py config                          - Generate default config file
"""
import sys
import argparse
from pathlib import Path

from config import Config
from audio_processor import AudioProcessor
from servo_controller import ServoController
from playback_engine import PlaybackEngine, SongLibrary, interactive_playback


def process_song(config: Config, audio_file: str, servo_assignments: dict = None):
    """
    Process a song - separate vocals and generate servo data.

    Args:
        config: Configuration object
        audio_file: Path to MP3/WAV file
        servo_assignments: Optional servo assignment configuration
    """
    print(f"\n=== Processing Song: {audio_file} ===\n")

    audio_file = Path(audio_file)
    if not audio_file.exists():
        print(f"Error: File not found: {audio_file}")
        return False

    # Create audio processor
    processor = AudioProcessor(config)

    try:
        # Process the song
        servo_data = processor.process_song(
            str(audio_file),
            servo_assignments=servo_assignments
        )

        print(f"\nProcessing complete!")
        print(f"Generated data for {len(servo_data)} servos")
        print(f"\nTo play this song, run:")
        print(f"  python main.py play {audio_file.stem}")

        return True

    except Exception as e:
        print(f"Error processing song: {e}")
        import traceback
        traceback.print_exc()
        return False


def play_song(config: Config, song_name: str, mock_mode: bool = False):
    """
    Play a processed song with servo movements.

    Args:
        config: Configuration object
        song_name: Name of the song to play
        mock_mode: If True, simulate servo control
    """
    print(f"\n=== Playing Song: {song_name} ===\n")

    # Initialize servo controller
    with ServoController(config, mock_mode=mock_mode) as controller:
        # Create playback engine
        engine = PlaybackEngine(config, controller)

        # Load song
        library = SongLibrary(config)

        if not library.has_song(song_name):
            print(f"Error: Song '{song_name}' not found")
            print("\nAvailable songs:")
            library.list_songs()
            return False

        audio_file = library.get_song_path(song_name)
        if not audio_file:
            print(f"Error: Could not find audio file for '{song_name}'")
            return False

        try:
            engine.load_song_from_processed(song_name, audio_file)
            engine.play(blocking=True)
            return True

        except Exception as e:
            print(f"Error playing song: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            engine.cleanup()


def test_servos(config: Config, mock_mode: bool = False):
    """
    Test all servos with a simple open/close pattern.

    Args:
        config: Configuration object
        mock_mode: If True, simulate servo control
    """
    print("\n=== Testing Servos ===\n")

    with ServoController(config, mock_mode=mock_mode) as controller:
        print("Testing each servo for 2 seconds...")
        controller.test_all(duration=2.0)
        print("\nServo test complete!")


def generate_config(output_file: str = "config/default_config.yaml"):
    """Generate a default configuration file."""
    print(f"Generating default configuration at: {output_file}")

    config = Config()
    config.save(output_file)

    print(f"\nConfiguration saved!")
    print(f"\nEdit {output_file} to customize:")
    print("  - GPIO pins for servos")
    print("  - Servo angle ranges")
    print("  - Audio processing parameters")


def main():
    parser = argparse.ArgumentParser(
        description="Singing Servos - Make your robots sing!",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'command',
        choices=['process', 'play', 'interactive', 'test', 'config'],
        help='Command to execute'
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='Input file (for process) or song name (for play)'
    )

    parser.add_argument(
        '--config',
        default=None,
        help='Path to configuration file'
    )

    parser.add_argument(
        '--mock',
        action='store_true',
        help='Run in mock mode (no actual servo control)'
    )

    parser.add_argument(
        '--all-servos',
        action='store_true',
        help='All servos sing together (default)'
    )

    parser.add_argument(
        '--servo-assignments',
        type=str,
        help='JSON string defining servo assignments, e.g., \'{"lead": ["servo1"], "backup": ["servo2", "servo3"]}\''
    )

    args = parser.parse_args()

    # Handle config generation
    if args.command == 'config':
        generate_config()
        return 0

    # Load configuration
    config = Config(args.config)

    # Parse servo assignments if provided
    servo_assignments = None
    if args.servo_assignments:
        import json
        try:
            servo_assignments = json.loads(args.servo_assignments)
        except json.JSONDecodeError as e:
            print(f"Error parsing servo assignments: {e}")
            return 1

    # Execute command
    if args.command == 'process':
        if not args.input:
            print("Error: Please provide an audio file to process")
            print("Usage: python main.py process <song.mp3>")
            return 1

        success = process_song(config, args.input, servo_assignments)
        return 0 if success else 1

    elif args.command == 'play':
        if not args.input:
            print("Error: Please provide a song name to play")
            print("Usage: python main.py play <song_name>")
            return 1

        success = play_song(config, args.input, mock_mode=args.mock)
        return 0 if success else 1

    elif args.command == 'interactive':
        with ServoController(config, mock_mode=args.mock) as controller:
            interactive_playback(config, controller)
        return 0

    elif args.command == 'test':
        test_servos(config, mock_mode=args.mock)
        return 0

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
