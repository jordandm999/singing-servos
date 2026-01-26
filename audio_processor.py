"""
Audio processing module for vocal separation and analysis.

This module handles:
- Separating vocals from music using Spleeter
- Analyzing vocal tracks for syllables and amplitude
- Generating servo movement data based on vocal patterns
"""
import numpy as np
import librosa
from pathlib import Path
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

try:
    from spleeter.separator import Separator
    SPLEETER_AVAILABLE = True
except ImportError:
    SPLEETER_AVAILABLE = False
    print("\n" + "="*60)
    print("WARNING: Spleeter not available")
    print("="*60)
    print("Spleeter doesn't work on ARM Macs (M1/M2/M3).")
    print("\nOptions:")
    print("1. Pre-separate vocals manually using online tools:")
    print("   - https://vocalremover.org")
    print("   - https://www.lalal.ai")
    print("2. Use an Intel Mac or Linux machine for processing")
    print("3. Process songs on your Raspberry Pi (slower)")
    print("\nYou can still use mock mode and test everything else!")
    print("="*60 + "\n")


class AudioProcessor:
    """Process audio files to extract vocal information for servo control."""

    def __init__(self, config):
        self.config = config
        self.sample_rate = config.audio['sample_rate']
        self.separator = None

        if SPLEETER_AVAILABLE:
            try:
                self.separator = Separator(config.audio['vocal_separation_model'])
            except Exception as e:
                print(f"Warning: Could not initialize Spleeter: {e}")

    def separate_vocals(self, audio_file: str, output_dir: str = None) -> str:
        """
        Separate vocals from music using Spleeter.

        Args:
            audio_file: Path to input MP3/WAV file
            output_dir: Directory to save separated vocals

        Returns:
            Path to the separated vocals file
        """
        if not self.separator:
            raise RuntimeError("Spleeter not available. Cannot separate vocals.")

        audio_file = Path(audio_file)
        if output_dir is None:
            output_dir = Path(self.config.paths['vocals_dir'])
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Separating vocals from {audio_file.name}...")

        # Spleeter will create a subdirectory with the song name
        self.separator.separate_to_file(
            str(audio_file),
            str(output_dir),
            codec='wav'
        )

        # Find the vocals file (Spleeter creates: output_dir/song_name/vocals.wav)
        song_name = audio_file.stem
        vocals_file = output_dir / song_name / 'vocals.wav'

        if not vocals_file.exists():
            raise FileNotFoundError(f"Expected vocals file not found: {vocals_file}")

        print(f"Vocals saved to: {vocals_file}")
        return str(vocals_file)

    def analyze_vocals(self, vocals_file: str) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Analyze vocals to extract timing and amplitude information.

        Args:
            vocals_file: Path to vocals WAV file

        Returns:
            Tuple of (time_array, amplitude_envelope, duration)
        """
        print(f"Analyzing vocals from {vocals_file}...")

        # Load vocals
        y, sr = librosa.load(vocals_file, sr=self.sample_rate)
        duration = librosa.get_duration(y=y, sr=sr)

        # Get amplitude envelope (how loud the vocals are over time)
        # Using RMS (Root Mean Square) energy
        hop_length = 512
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

        # Create time array
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

        # Normalize amplitude to 0-1 range
        rms_normalized = rms / (np.max(rms) + 1e-8)

        return times, rms_normalized, duration

    def detect_syllables(self, times: np.ndarray, amplitude: np.ndarray) -> np.ndarray:
        """
        Detect syllable onsets in the vocal track.

        Args:
            times: Time array
            amplitude: Amplitude envelope

        Returns:
            Array of syllable onset times
        """
        threshold = self.config.audio['syllable_threshold']

        # Find onset points where amplitude crosses threshold
        onsets = []
        is_above = False

        for i in range(len(amplitude)):
            if amplitude[i] > threshold and not is_above:
                onsets.append(times[i])
                is_above = True
            elif amplitude[i] <= threshold:
                is_above = False

        return np.array(onsets)

    def separate_vocal_parts(self, vocals_file: str, num_parts: int = 1) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """
        Attempt to separate different vocal parts (for multi-servo assignment).

        For now, this uses simple stereo channel separation or pitch-based separation.

        Args:
            vocals_file: Path to vocals file
            num_parts: Number of vocal parts to separate (1-3)

        Returns:
            Dictionary mapping part names to (times, amplitude) tuples
        """
        if num_parts == 1:
            # Single part - use all vocals
            times, amplitude, _ = self.analyze_vocals(vocals_file)
            return {'all': (times, amplitude)}

        # Load stereo vocals
        y, sr = librosa.load(vocals_file, sr=self.sample_rate, mono=False)

        # If stereo, try to use channels
        if y.ndim == 2 and num_parts == 2:
            parts = {}
            for i, channel in enumerate(['left', 'right']):
                hop_length = 512
                rms = librosa.feature.rms(y=y[i:i+1], hop_length=hop_length)[0]
                times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
                rms_normalized = rms / (np.max(rms) + 1e-8)
                parts[channel] = (times, rms_normalized)
            return parts

        # For 3 parts or mono source, use pitch-based separation
        y_mono = librosa.to_mono(y) if y.ndim == 2 else y

        # Extract pitch
        pitches, magnitudes = librosa.piptrack(y=y_mono, sr=sr)

        # Get pitch over time
        pitch_over_time = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            pitch_over_time.append(pitch)

        pitch_over_time = np.array(pitch_over_time)

        # Separate into parts based on pitch ranges
        # Low, Mid, High (simple approach)
        hop_length = 512
        rms = librosa.feature.rms(y=y_mono, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

        # This is a simplified separation - could be improved
        parts = {}
        if num_parts == 3:
            # Split into low/mid/high based on pitch percentiles
            valid_pitches = pitch_over_time[pitch_over_time > 0]
            if len(valid_pitches) > 0:
                low_thresh = np.percentile(valid_pitches, 33)
                high_thresh = np.percentile(valid_pitches, 67)

                low_mask = (pitch_over_time > 0) & (pitch_over_time <= low_thresh)
                mid_mask = (pitch_over_time > low_thresh) & (pitch_over_time <= high_thresh)
                high_mask = pitch_over_time > high_thresh

                for name, mask in [('low', low_mask), ('mid', mid_mask), ('high', high_mask)]:
                    masked_rms = rms * mask[:len(rms)]
                    rms_normalized = masked_rms / (np.max(rms) + 1e-8)
                    parts[name] = (times, rms_normalized)
            else:
                # Fallback to same part for all
                rms_normalized = rms / (np.max(rms) + 1e-8)
                parts = {'all': (times, rms_normalized)}

        return parts if parts else {'all': (times, rms / (np.max(rms) + 1e-8))}

    def generate_servo_data(self, times: np.ndarray, amplitude: np.ndarray,
                           servo_name: str = 'default') -> np.ndarray:
        """
        Generate servo position data from vocal amplitude.

        Args:
            times: Time array
            amplitude: Amplitude envelope (0-1)
            servo_name: Name of servo (for custom calibration)

        Returns:
            Array of (time, position) pairs where position is 0-1 (0=closed, 1=open)
        """
        # Apply smoothing
        window = int(self.config.audio['smoothing_window'] * self.sample_rate / 512)
        if window > 1:
            kernel = np.ones(window) / window
            amplitude_smooth = np.convolve(amplitude, kernel, mode='same')
        else:
            amplitude_smooth = amplitude

        # Create servo positions (0 = closed, 1 = open)
        # Map amplitude to mouth opening with some minimum threshold
        threshold = self.config.audio['syllable_threshold']
        positions = np.where(amplitude_smooth > threshold, amplitude_smooth, 0)

        # Combine into (time, position) pairs
        servo_data = np.column_stack([times, positions])

        return servo_data

    def process_song(self, audio_file: str, servo_assignments: Dict[str, List[str]] = None) -> Dict[str, np.ndarray]:
        """
        Complete processing pipeline for a song.

        Args:
            audio_file: Path to MP3/WAV file
            servo_assignments: Dictionary mapping part names to servo names
                              e.g., {"lead": ["servo1"], "backup": ["servo2", "servo3"]}

        Returns:
            Dictionary mapping servo names to their movement data arrays
        """
        # Default: all servos do the same thing
        if servo_assignments is None:
            servo_assignments = {"all": [s.name for s in self.config.servos]}

        # Step 1: Separate vocals
        vocals_file = self.separate_vocals(audio_file)

        # Step 2: Separate into parts if needed
        num_parts = len(servo_assignments)
        vocal_parts = self.separate_vocal_parts(vocals_file, num_parts)

        # Step 3: Generate servo data for each servo
        servo_data_map = {}

        # Map parts to servos
        for part_name, servo_names in servo_assignments.items():
            if part_name in vocal_parts:
                times, amplitude = vocal_parts[part_name]
            elif 'all' in vocal_parts:
                times, amplitude = vocal_parts['all']
            else:
                # Use first available part
                times, amplitude = list(vocal_parts.values())[0]

            # Generate data for each servo in this part
            for servo_name in servo_names:
                servo_data = self.generate_servo_data(times, amplitude, servo_name)
                servo_data_map[servo_name] = servo_data

        # Save servo data
        output_dir = Path(self.config.paths['servo_data_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        song_name = Path(audio_file).stem
        for servo_name, data in servo_data_map.items():
            output_file = output_dir / f"{song_name}_{servo_name}.npy"
            np.save(output_file, data)
            print(f"Saved servo data: {output_file}")

        return servo_data_map
