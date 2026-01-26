#!/usr/bin/env python3
"""
Manual Servo Control

Interactive tool for testing servos manually.
Good for testing your setup before processing songs.
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from servo_controller import ServoController


def main():
    """Interactive manual control."""
    print("\n=== Manual Servo Control ===\n")
    print("Commands:")
    print("  <servo_name> <position>  - Set servo position (0.0 - 1.0)")
    print("  all <position>           - Set all servos to position")
    print("  close                    - Close all servos")
    print("  test <servo_name>        - Test a specific servo")
    print("  list                     - List available servos")
    print("  quit                     - Exit")
    print()

    config = Config()

    print("Available servos:")
    for servo in config.servos:
        print(f"  - {servo.name} (GPIO {servo.gpio_pin})")
    print()

    with ServoController(config, mock_mode=False) as controller:
        while True:
            try:
                command = input("> ").strip().lower()

                if not command:
                    continue

                if command in ['quit', 'exit', 'q']:
                    break

                if command == 'close':
                    controller.close_all()
                    print("All servos closed")
                    continue

                if command == 'list':
                    print("Available servos:")
                    for servo in config.servos:
                        print(f"  - {servo.name} (GPIO {servo.gpio_pin})")
                    continue

                parts = command.split()

                if len(parts) == 2:
                    servo_name, position_str = parts

                    try:
                        position = float(position_str)
                    except ValueError:
                        print(f"Invalid position: {position_str}")
                        continue

                    if servo_name == 'all':
                        for s in config.servos:
                            controller.set_position(s.name, position)
                        print(f"All servos set to {position}")
                    elif servo_name in [s.name for s in config.servos]:
                        controller.set_position(servo_name, position)
                        print(f"{servo_name} set to {position}")
                    else:
                        print(f"Unknown servo: {servo_name}")

                elif len(parts) == 2 and parts[0] == 'test':
                    servo_name = parts[1]
                    if servo_name in [s.name for s in config.servos]:
                        controller.test_servo(servo_name)
                    else:
                        print(f"Unknown servo: {servo_name}")

                else:
                    print("Invalid command. Try:")
                    print("  servo1 0.5")
                    print("  all 0.8")
                    print("  test servo1")
                    print("  close")

            except KeyboardInterrupt:
                print()
                break

    print("\nExiting...")


if __name__ == '__main__':
    main()
