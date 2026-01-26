"""
Playback engine for synchronizing audio and servo movements.

This module coordinates playing the audio file through speakers while
simultaneously controlling servos based on pre-processed movement data.
"""
import time
import pygame
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from servo_controller import ServoController, ServoPlayback


class PlaybackEngine:
    """Synchronize audio playback with servo movements."""

    def __init__(self, config, servo_controller: ServoController):
        self.config = config
        self.servo_controller = servo_controller
        self.servo_playback = ServoPlayback(servo_controller)

        # Initialize pygame mixer for audio playback
        pygame.mixer.init(frequency=config.audio['sample_rate'])
        self.current_song = None
        self.is_playing = False

    def load_song(self, audio_file: str, servo_data_map: Dict[str, np.ndarray]):
        """
        Load a song and its servo data for playback.

        Args:
            audio_file: Path to audio file (MP3/WAV)
            servo_data_map: Dictionary mapping servo names to movement data
        """
        print(f"Loading song: {audio_file}")

        # Load audio
        pygame.mixer.music.load(audio_file)
        self.current_song = audio_file

        # Load servo data
        self.servo_playback.load_servo_data(servo_data_map)

        print("Song loaded and ready to play")

    def load_song_from_processed(self, song_name: str, original_audio: str):
        """
        Load a song using pre-processed servo data files.

        Args:
            song_name: Name of the song (stem of filename)
            original_audio: Path to original audio file to play
        """
        # Find servo data files
        servo_data_dir = Path(self.config.paths['servo_data_dir'])
        servo_data_map = {}

        for servo_config in self.config.servos:
            servo_file = servo_data_dir / f"{song_name}_{servo_config.name}.npy"

            if servo_file.exists():
                data = np.load(servo_file)
                servo_data_map[servo_config.name] = data
                print(f"Loaded data for {servo_config.name}: {len(data)} frames")
            else:
                print(f"Warning: No data file found for {servo_config.name}")

        if not servo_data_map:
            raise FileNotFoundError(f"No servo data found for song '{song_name}'")

        self.load_song(original_audio, servo_data_map)

    def play(self, blocking: bool = True):
        """
        Start playback of the loaded song.

        Args:
            blocking: If True, block until playback finishes
        """
        if self.current_song is None:
            print("No song loaded")
            return

        print("Starting playback...")
        self.is_playing = True

        # Start audio playback
        pygame.mixer.music.play()
        start_time = time.time()

        try:
            # Main playback loop
            while self.is_playing and pygame.mixer.music.get_busy():
                current_time = time.time() - start_time

                # Update servo positions
                self.servo_playback.update(current_time)

                # Small sleep to prevent busy-waiting
                time.sleep(0.01)  # Update servos at ~100 Hz

                if not blocking:
                    break

            if blocking:
                print("Playback complete")
                self.servo_playback.reset()

        except KeyboardInterrupt:
            print("\nPlayback interrupted")
            self.stop()

    def stop(self):
        """Stop playback."""
        self.is_playing = False
        pygame.mixer.music.stop()
        self.servo_playback.reset()
        print("Playback stopped")

    def pause(self):
        """Pause playback."""
        if self.is_playing:
            pygame.mixer.music.pause()
            print("Playback paused")

    def unpause(self):
        """Resume playback."""
        if self.is_playing:
            pygame.mixer.music.unpause()
            print("Playback resumed")

    def get_position(self) -> float:
        """Get current playback position in seconds."""
        return pygame.mixer.music.get_pos() / 1000.0

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        pygame.mixer.quit()


class SongLibrary:
    """Manage a library of processed songs."""

    def __init__(self, config):
        self.config = config
        self.songs = {}
        self._scan_library()

    def _scan_library(self):
        """Scan for processed songs."""
        servo_data_dir = Path(self.config.paths['servo_data_dir'])

        if not servo_data_dir.exists():
            return

        # Find all unique song names from servo data files
        servo_files = list(servo_data_dir.glob("*.npy"))
        song_names = set()

        for f in servo_files:
            # Format: songname_servoname.npy
            parts = f.stem.rsplit('_', 1)
            if len(parts) == 2:
                song_name = parts[0]
                song_names.add(song_name)

        self.songs = {name: None for name in song_names}
        print(f"Found {len(self.songs)} processed songs in library")

    def list_songs(self):
        """List all available songs."""
        if not self.songs:
            print("No processed songs found")
            return

        print("Available songs:")
        for i, song_name in enumerate(sorted(self.songs.keys()), 1):
            print(f"  {i}. {song_name}")

    def get_song_path(self, song_name: str) -> Optional[str]:
        """
        Find the original audio file for a song.

        Args:
            song_name: Name of the song

        Returns:
            Path to audio file if found, None otherwise
        """
        songs_dir = Path(self.config.paths['songs_dir'])

        # Try common extensions
        for ext in ['.mp3', '.wav', '.m4a']:
            audio_file = songs_dir / f"{song_name}{ext}"
            if audio_file.exists():
                return str(audio_file)

        # Try in processed vocals directory
        vocals_dir = Path(self.config.paths['vocals_dir'])
        vocals_file = vocals_dir / song_name / 'vocals.wav'
        if vocals_file.exists():
            # Could play vocals only
            return str(vocals_file)

        return None

    def has_song(self, song_name: str) -> bool:
        """Check if a song exists in the library."""
        return song_name in self.songs


def interactive_playback(config, servo_controller: ServoController):
    """
    Interactive playback mode - let user choose songs to play.

    Args:
        config: Configuration object
        servo_controller: Initialized servo controller
    """
    library = SongLibrary(config)
    engine = PlaybackEngine(config, servo_controller)

    print("\n=== Singing Servos - Interactive Playback ===\n")
    library.list_songs()

    if not library.songs:
        print("\nNo songs available. Process some songs first using:")
        print("  python main.py process <song.mp3>")
        return

    try:
        while True:
            print("\nEnter song name to play (or 'quit' to exit):")
            choice = input("> ").strip()

            if choice.lower() in ['quit', 'exit', 'q']:
                break

            if library.has_song(choice):
                audio_file = library.get_song_path(choice)
                if audio_file:
                    try:
                        engine.load_song_from_processed(choice, audio_file)
                        engine.play(blocking=True)
                    except Exception as e:
                        print(f"Error playing song: {e}")
                else:
                    print(f"Could not find audio file for '{choice}'")
            else:
                print(f"Song '{choice}' not found in library")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        engine.cleanup()
