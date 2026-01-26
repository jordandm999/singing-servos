#!/usr/bin/env python3
"""
Servo Calibration Tool

Use this script to find the correct angle ranges for your servos.
This helps you set the right open_angle and closed_angle values for your robot mouths.
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from servo_controller import ServoController


def calibrate_servo(controller: ServoController, servo_name: str):
    """
    Interactive calibration for a single servo.

    Args:
        controller: Servo controller instance
        servo_name: Name of servo to calibrate
    """
    print(f"\n=== Calibrating {servo_name} ===\n")

    servo = controller.servos.get(servo_name)
    if not servo:
        print(f"Error: Servo '{servo_name}' not found")
        return

    config = servo['config']

    print("This will help you find the right angles for your servo.")
    print("Watch the servo and note which positions look best.\n")

    print("Testing closed position (position = 0.0)...")
    controller.set_position(servo_name, 0.0)
    time.sleep(2)

    print("Testing open position (position = 1.0)...")
    controller.set_position(servo_name, 1.0)
    time.sleep(2)

    print("\nNow let's test intermediate positions...")
    for pos in [0.25, 0.5, 0.75]:
        print(f"Position {pos}...")
        controller.set_position(servo_name, pos)
        time.sleep(1.5)

    # Return to closed
    controller.set_position(servo_name, 0.0)

    print("\n=== Calibration Questions ===\n")
    print(f"Current settings for {servo_name}:")
    print(f"  closed_angle: {config.closed_angle}°")
    print(f"  open_angle: {config.open_angle}°")
    print(f"  GPIO pin: {config.gpio_pin}")
    print()

    print("Questions:")
    print("1. Did the servo move through a good range?")
    print("2. Was the 'closed' position actually closed?")
    print("3. Was the 'open' position appropriate (not too far)?")
    print()
    print("If not, you may need to adjust the angles in your config file.")
    print("Common adjustments:")
    print("  - If reversed: swap closed_angle and open_angle")
    print("  - If too much movement: reduce the difference between angles")
    print("  - If too little movement: increase the difference")
    print()


def main():
    """Main calibration routine."""
    print("\n=== Servo Calibration Tool ===\n")

    # Load configuration
    config = Config()

    print(f"Found {len(config.servos)} servos in configuration:")
    for i, servo in enumerate(config.servos, 1):
        print(f"  {i}. {servo.name} (GPIO {servo.gpio_pin})")
    print()

    # Ask which servo to calibrate
    print("Which servo do you want to calibrate?")
    print("Enter number, name, or 'all' for all servos, or 'quit' to exit")

    with ServoController(config, mock_mode=False) as controller:
        while True:
            choice = input("\n> ").strip().lower()

            if choice in ['quit', 'exit', 'q']:
                break

            if choice == 'all':
                for servo in config.servos:
                    calibrate_servo(controller, servo.name)
                    input("\nPress Enter to continue to next servo...")
                break

            # Try by number
            try:
                servo_idx = int(choice) - 1
                if 0 <= servo_idx < len(config.servos):
                    servo_name = config.servos[servo_idx].name
                    calibrate_servo(controller, servo_name)
                    continue
            except ValueError:
                pass

            # Try by name
            servo_names = [s.name for s in config.servos]
            if choice in servo_names:
                calibrate_servo(controller, choice)
            else:
                print(f"Unknown servo: {choice}")
                print("Try: servo1, servo2, servo3, all, or quit")

    print("\nCalibration complete!")
    print("\nTo update your configuration:")
    print("1. Edit config/default_config.yaml")
    print("2. Adjust the closed_angle and open_angle values")
    print("3. Run this script again to verify")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCalibration interrupted")
        sys.exit(0)
