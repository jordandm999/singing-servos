"""
Configuration management for Singing Servos project.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class ServoConfig:
    """Configuration for a single servo."""

    def __init__(self, name: str, gpio_pin: int, min_pulse: int = 500,
                 max_pulse: int = 2500, closed_angle: int = 0, open_angle: int = 90):
        self.name = name
        self.gpio_pin = gpio_pin
        self.min_pulse = min_pulse  # Microseconds
        self.max_pulse = max_pulse  # Microseconds
        self.closed_angle = closed_angle
        self.open_angle = open_angle

    @classmethod
    def from_dict(cls, data: dict) -> 'ServoConfig':
        return cls(**data)


class SongConfig:
    """Configuration for how a song maps to servos."""

    def __init__(self, name: str, file_path: str, servo_assignments: Optional[Dict[str, List[str]]] = None):
        self.name = name
        self.file_path = file_path
        # Maps servo names to their role: e.g., {"lead": ["servo1"], "backup": ["servo2", "servo3"]}
        self.servo_assignments = servo_assignments or {"all": []}

    @classmethod
    def from_dict(cls, data: dict) -> 'SongConfig':
        return cls(**data)


class Config:
    """Main configuration class."""

    DEFAULT_CONFIG = {
        'servos': [
            # Pulse range 500-1200 gives roughly 0-60° on SG90 servos
            {'name': 'servo1', 'gpio_pin': 17, 'min_pulse': 500, 'max_pulse': 1200,
             'closed_angle': 0, 'open_angle': 60},
            {'name': 'servo2', 'gpio_pin': 27, 'min_pulse': 500, 'max_pulse': 1200,
             'closed_angle': 0, 'open_angle': 60},
            {'name': 'servo3', 'gpio_pin': 22, 'min_pulse': 500, 'max_pulse': 1200,
             'closed_angle': 0, 'open_angle': 60},
        ],
        'audio': {
            'sample_rate': 44100,
            'vocal_separation_model': 'spleeter:2stems',  # or 'spleeter:4stems' or 'spleeter:5stems'
            'syllable_threshold': 0.02,  # Minimum amplitude to detect as syllable
            'smoothing_window': 0.05,  # Seconds to smooth servo movements
        },
        'paths': {
            'songs_dir': 'songs',
            'processed_dir': 'processed',
            'vocals_dir': 'processed/vocals',
            'servo_data_dir': 'processed/servo_data',
        }
    }

    def __init__(self, config_file: Optional[str] = None):
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            config_data = self.DEFAULT_CONFIG

        # Parse servos
        self.servos = [ServoConfig.from_dict(s) for s in config_data['servos']]
        self.audio = config_data['audio']
        self.paths = config_data['paths']

        # Create directories if they don't exist
        for path in self.paths.values():
            Path(path).mkdir(parents=True, exist_ok=True)

    def get_servo(self, name: str) -> Optional[ServoConfig]:
        """Get servo configuration by name."""
        for servo in self.servos:
            if servo.name == name:
                return servo
        return None

    def save(self, file_path: str):
        """Save configuration to YAML file."""
        config_data = {
            'servos': [
                {
                    'name': s.name,
                    'gpio_pin': s.gpio_pin,
                    'min_pulse': s.min_pulse,
                    'max_pulse': s.max_pulse,
                    'closed_angle': s.closed_angle,
                    'open_angle': s.open_angle
                }
                for s in self.servos
            ],
            'audio': self.audio,
            'paths': self.paths
        }

        with open(file_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)


if __name__ == '__main__':
    # Generate default config file
    config = Config()
    config.save('config/default_config.yaml')
    print("Generated default configuration at config/default_config.yaml")
