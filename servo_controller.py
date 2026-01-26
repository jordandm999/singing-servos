"""
Servo controller module for Raspberry Pi.

This module handles low-level servo control via GPIO pins using pigpio.
"""
import time
import numpy as np
from typing import Dict, Optional

try:
    import pigpio
    PIGPIO_AVAILABLE = True
except ImportError:
    PIGPIO_AVAILABLE = False
    print("Warning: pigpio not available. Run 'sudo pigpiod' on Raspberry Pi.")


class ServoController:
    """Control servos connected to Raspberry Pi GPIO pins."""

    def __init__(self, config, mock_mode: bool = False):
        """
        Initialize servo controller.

        Args:
            config: Configuration object
            mock_mode: If True, simulate servo control without hardware
        """
        self.config = config
        self.mock_mode = mock_mode or not PIGPIO_AVAILABLE
        self.pi = None
        self.servos = {}

        if not self.mock_mode:
            try:
                self.pi = pigpio.pi()
                if not self.pi.connected:
                    print("Warning: Could not connect to pigpio daemon. Using mock mode.")
                    self.mock_mode = True
            except Exception as e:
                print(f"Warning: pigpio initialization failed: {e}. Using mock mode.")
                self.mock_mode = True

        # Initialize servos
        for servo_config in config.servos:
            self.add_servo(servo_config)

        if self.mock_mode:
            print("Running in MOCK MODE - no actual servo control")

    def add_servo(self, servo_config):
        """Add a servo to the controller."""
        self.servos[servo_config.name] = {
            'config': servo_config,
            'current_position': 0.0,  # 0 = closed, 1 = open
        }

        if not self.mock_mode:
            # Set initial position (closed)
            self._set_servo_angle(servo_config, servo_config.closed_angle)

        print(f"Initialized servo '{servo_config.name}' on GPIO {servo_config.gpio_pin}")

    def _set_servo_angle(self, servo_config, angle: float):
        """
        Set servo to specific angle using pulse width.

        Args:
            servo_config: Servo configuration
            angle: Angle in degrees
        """
        if self.mock_mode:
            return

        # Convert angle to pulse width
        # pulse_width = min_pulse + (angle / max_angle) * (max_pulse - min_pulse)
        angle_range = servo_config.open_angle - servo_config.closed_angle
        pulse_range = servo_config.max_pulse - servo_config.min_pulse

        if angle_range != 0:
            pulse_width = servo_config.min_pulse + (angle / angle_range) * pulse_range
        else:
            pulse_width = servo_config.min_pulse

        # Clamp pulse width
        pulse_width = max(servo_config.min_pulse, min(servo_config.max_pulse, pulse_width))

        self.pi.set_servo_pulsewidth(servo_config.gpio_pin, pulse_width)

    def set_position(self, servo_name: str, position: float):
        """
        Set servo position.

        Args:
            servo_name: Name of servo
            position: Position from 0 (closed) to 1 (open)
        """
        if servo_name not in self.servos:
            print(f"Warning: Unknown servo '{servo_name}'")
            return

        servo = self.servos[servo_name]
        config = servo['config']

        # Clamp position
        position = max(0.0, min(1.0, position))

        # Convert position to angle
        angle = config.closed_angle + position * (config.open_angle - config.closed_angle)

        # Update servo
        if not self.mock_mode:
            self._set_servo_angle(config, angle)
        else:
            # In mock mode, just print
            if abs(position - servo['current_position']) > 0.1:  # Only print significant changes
                print(f"  [{servo_name}] position: {position:.2f} (angle: {angle:.1f}°)")

        servo['current_position'] = position

    def set_all_positions(self, positions: Dict[str, float]):
        """
        Set positions for multiple servos at once.

        Args:
            positions: Dictionary mapping servo names to positions (0-1)
        """
        for servo_name, position in positions.items():
            self.set_position(servo_name, position)

    def close_all(self):
        """Close all servo mouths."""
        for servo_name in self.servos:
            self.set_position(servo_name, 0.0)

    def test_servo(self, servo_name: str, duration: float = 2.0):
        """
        Test a servo by opening and closing it.

        Args:
            servo_name: Name of servo to test
            duration: Duration of test in seconds
        """
        print(f"Testing servo '{servo_name}'...")

        steps = 20
        for i in range(steps):
            # Sine wave pattern
            position = (np.sin(i * 2 * np.pi / steps) + 1) / 2
            self.set_position(servo_name, position)
            time.sleep(duration / steps)

        # Return to closed
        self.set_position(servo_name, 0.0)
        print(f"Test complete for '{servo_name}'")

    def test_all(self, duration: float = 2.0):
        """Test all servos sequentially."""
        for servo_name in self.servos:
            self.test_servo(servo_name, duration)

    def cleanup(self):
        """Clean up GPIO resources."""
        print("Closing all servos...")
        self.close_all()

        if not self.mock_mode and self.pi:
            time.sleep(0.5)
            # Stop all servo pulses
            for servo_name, servo in self.servos.items():
                config = servo['config']
                self.pi.set_servo_pulsewidth(config.gpio_pin, 0)

            self.pi.stop()
            print("GPIO cleanup complete")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class ServoPlayback:
    """Handle real-time servo playback synchronized with audio."""

    def __init__(self, controller: ServoController):
        self.controller = controller
        self.servo_data = {}  # Maps servo names to (times, positions) arrays
        self.start_time = None

    def load_servo_data(self, servo_data_map: Dict[str, np.ndarray]):
        """
        Load pre-processed servo movement data.

        Args:
            servo_data_map: Dictionary mapping servo names to their (time, position) arrays
        """
        self.servo_data = servo_data_map
        print(f"Loaded servo data for {len(servo_data_map)} servos")

    def update(self, current_time: float):
        """
        Update servo positions based on current playback time.

        Args:
            current_time: Current time in seconds since playback started
        """
        positions = {}

        for servo_name, data in self.servo_data.items():
            if len(data) == 0:
                positions[servo_name] = 0.0
                continue

            times = data[:, 0]
            pos_values = data[:, 1]

            # Find the appropriate position via interpolation
            if current_time <= times[0]:
                position = pos_values[0]
            elif current_time >= times[-1]:
                position = pos_values[-1]
            else:
                # Linear interpolation
                position = np.interp(current_time, times, pos_values)

            positions[servo_name] = position

        # Update all servos
        self.controller.set_all_positions(positions)

    def reset(self):
        """Reset playback to beginning."""
        self.start_time = None
        self.controller.close_all()
