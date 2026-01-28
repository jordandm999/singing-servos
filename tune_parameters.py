#!/usr/bin/env python3
"""
Parameter Tuning Tool

Adjust vocal detection sensitivity and smoothing to get better servo movements.

Usage:
    python3 tune_parameters.py processed/vocals/my_son_john/vocals.wav
"""
import sys
import numpy as np
import librosa
import matplotlib
matplotlib.use('TkAgg')  # For macOS
import matplotlib.pyplot as plt
from pathlib import Path


def analyze_with_params(vocals_file, threshold=0.02, smoothing_window=0.05, sample_rate=44100):
    """Analyze vocals with given parameters and visualize."""

    print(f"\nAnalyzing with:")
    print(f"  Threshold: {threshold}")
    print(f"  Smoothing: {smoothing_window}s")

    # Load vocals
    y, sr = librosa.load(vocals_file, sr=sample_rate)
    duration = librosa.get_duration(y=y, sr=sr)

    # Get amplitude envelope
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    # Normalize
    rms_normalized = rms / (np.max(rms) + 1e-8)

    # Apply smoothing
    window_samples = int(smoothing_window * sample_rate / hop_length)
    if window_samples > 1:
        kernel = np.ones(window_samples) / window_samples
        rms_smooth = np.convolve(rms_normalized, kernel, mode='same')
    else:
        rms_smooth = rms_normalized

    # Apply threshold
    positions = np.where(rms_smooth > threshold, rms_smooth, 0)

    # Plot
    plt.figure(figsize=(15, 8))

    # Raw amplitude
    plt.subplot(3, 1, 1)
    plt.plot(times, rms_normalized, label='Raw Amplitude', alpha=0.7)
    plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold ({threshold})')
    plt.ylabel('Amplitude')
    plt.title('Raw Vocal Amplitude')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Smoothed amplitude
    plt.subplot(3, 1, 2)
    plt.plot(times, rms_smooth, label=f'Smoothed (window={smoothing_window}s)', color='orange')
    plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold ({threshold})')
    plt.ylabel('Amplitude')
    plt.title('Smoothed Amplitude')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Final servo positions
    plt.subplot(3, 1, 3)
    plt.plot(times, positions, label='Servo Position (0=closed, 1=open)', color='green', linewidth=2)
    plt.ylabel('Servo Position')
    plt.xlabel('Time (seconds)')
    plt.title('Final Servo Movements')
    plt.ylim(-0.1, 1.1)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Print statistics
    active_time = np.sum(positions > 0) / len(positions) * duration
    print(f"\nStatistics:")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Servo active time: {active_time:.2f}s ({active_time/duration*100:.1f}%)")
    print(f"  Max position: {np.max(positions):.2f}")
    print(f"  Avg position (when active): {np.mean(positions[positions > 0]):.2f}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tune_parameters.py <vocals.wav>")
        print("\nExample:")
        print("  python3 tune_parameters.py processed/vocals/my_son_john/vocals.wav")
        sys.exit(1)

    vocals_file = sys.argv[1]

    if not Path(vocals_file).exists():
        print(f"Error: File not found: {vocals_file}")
        sys.exit(1)

    print("=" * 60)
    print("PARAMETER TUNING TOOL")
    print("=" * 60)
    print("\nThis tool helps you find the best settings for your song.")
    print("Try different values to see how they affect servo movements.\n")

    while True:
        print("\nCurrent settings:")
        print("  1. Threshold (lower = more sensitive)")
        print("  2. Smoothing window (lower = more responsive)")
        print("  3. Analyze with current settings")
        print("  4. Save settings to config")
        print("  5. Quit")

        choice = input("\nChoose (1-5): ").strip()

        if choice == '1':
            threshold_input = input("Enter threshold (0.01-0.1, default 0.02): ").strip()
            try:
                threshold = float(threshold_input)
            except ValueError:
                threshold = 0.02
        elif choice == '2':
            smooth_input = input("Enter smoothing window in seconds (0.01-0.2, default 0.05): ").strip()
            try:
                smoothing_window = float(smooth_input)
            except ValueError:
                smoothing_window = 0.05
        elif choice == '3':
            analyze_with_params(vocals_file, threshold, smoothing_window)
        elif choice == '4':
            print(f"\nAdd these to your config.yaml:")
            print(f"  syllable_threshold: {threshold}")
            print(f"  smoothing_window: {smoothing_window}")
        elif choice == '5':
            break
        else:
            # Default: analyze with recommended settings for sea shanty
            print("\nTrying recommended settings for sea shanty:")
            threshold = 0.015  # More sensitive
            smoothing_window = 0.02  # More responsive
            analyze_with_params(vocals_file, threshold, smoothing_window)


if __name__ == '__main__':
    threshold = 0.02
    smoothing_window = 0.05
    main()
