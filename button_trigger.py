#!/usr/bin/env python3
"""
Button Trigger - Play random songs with a push button!

This script runs continuously and waits for a button press.
When pressed, it plays a random processed song from the library.

Wiring:
  - One leg of button to GPIO 4 (pin 7)
  - Other leg of button to GND (pin 9)
  - Uses internal pull-up resistor, so no external resistor needed

Usage:
    python3 button_trigger.py

To run on boot, add to /etc/rc.local or create a systemd service.
"""
import sys
import time
import random
import signal

try:
    import pigpio
except ImportError:
    print("Error: pigpio not available. Make sure you're on a Raspberry Pi.")
    print("Install with: sudo apt install pigpio python3-pigpio")
    print("Start daemon with: sudo pigpiod")
    sys.exit(1)

from config import Config
from servo_controller import ServoController
from playback_engine import PlaybackEngine, SongLibrary


# CONFIGURATION
BUTTON_PIN = 4          # GPIO 4 (physical pin 7)
DEBOUNCE_TIME = 0.3     # Seconds to wait between button presses
LED_PIN = None          # Optional: GPIO pin for status LED (e.g., 25)


class ButtonPlayer:
    """Handle button presses and play random songs."""

    def __init__(self, config, mock_mode=False):
        self.config = config
        self.mock_mode = mock_mode
        self.playing = False
        self.last_press_time = 0

        # Initialize pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon. Run: sudo pigpiod")

        # Set up button with internal pull-up resistor
        self.pi.set_mode(BUTTON_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(BUTTON_PIN, pigpio.PUD_UP)

        # Optional LED for status
        if LED_PIN:
            self.pi.set_mode(LED_PIN, pigpio.OUTPUT)
            self.pi.write(LED_PIN, 0)

        # Initialize servo controller
        self.servo_controller = ServoController(config, mock_mode=mock_mode)

        # Initialize playback engine
        self.engine = PlaybackEngine(config, self.servo_controller)

        # Load song library
        self.library = SongLibrary(config)

        print(f"\nFound {len(self.library.songs)} songs in library:")
        self.library.list_songs()

    def flash_led(self, times=2, duration=0.1):
        """Flash the status LED."""
        if not LED_PIN:
            return
        for _ in range(times):
            self.pi.write(LED_PIN, 1)
            time.sleep(duration)
            self.pi.write(LED_PIN, 0)
            time.sleep(duration)

    def play_random_song(self):
        """Play a random song from the library."""
        if not self.library.songs:
            print("No songs available!")
            return

        # Pick a random song
        song_name = random.choice(list(self.library.songs.keys()))
        audio_file = self.library.get_song_path(song_name)

        if not audio_file:
            print(f"Could not find audio file for '{song_name}'")
            return

        print(f"\n{'='*60}")
        print(f"Playing: {song_name}")
        print(f"{'='*60}\n")

        # Flash LED to indicate song starting
        self.flash_led(times=3)

        try:
            self.playing = True

            # Turn on LED while playing
            if LED_PIN:
                self.pi.write(LED_PIN, 1)

            # Load and play song
            self.engine.load_song_from_processed(song_name, audio_file)
            self.engine.play(blocking=True)

        except Exception as e:
            print(f"Error playing song: {e}")
        finally:
            self.playing = False
            if LED_PIN:
                self.pi.write(LED_PIN, 0)

        print("\nPlayback complete. Waiting for button press...")

    def check_button(self):
        """Check if button is pressed (active low due to pull-up)."""
        return self.pi.read(BUTTON_PIN) == 0

    def run(self):
        """Main loop - wait for button presses."""
        print("\n" + "="*60)
        print("SINGING SERVOS - Button Trigger Mode")
        print("="*60)
        print(f"\nButton on GPIO {BUTTON_PIN} (physical pin 7)")
        print("Press the button to play a random song!")
        print("Press Ctrl+C to exit\n")

        try:
            while True:
                # Check if button is pressed
                if self.check_button():
                    current_time = time.time()

                    # Debounce - ignore rapid presses
                    if current_time - self.last_press_time > DEBOUNCE_TIME:
                        self.last_press_time = current_time

                        if not self.playing:
                            self.play_random_song()
                        else:
                            print("Already playing a song...")

                time.sleep(0.05)  # Check button 20 times per second

        except KeyboardInterrupt:
            print("\n\nShutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        self.servo_controller.cleanup()
        self.engine.cleanup()

        if LED_PIN:
            self.pi.write(LED_PIN, 0)

        self.pi.stop()
        print("Cleanup complete")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Play random songs with a button press")
    parser.add_argument('--mock', action='store_true', help='Run in mock mode (for testing)')
    parser.add_argument('--config', default=None, help='Path to config file')
    args = parser.parse_args()

    # Load configuration
    config = Config(args.config)

    # Create button player
    player = ButtonPlayer(config, mock_mode=args.mock)

    # Run main loop
    player.run()


if __name__ == '__main__':
    main()
