import os, sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --- Paths (absolute, based on script location) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "..", "logger", "data")
DATA_FILE = os.path.join(DATA_DIR, "SOUND.txt")

CHARTS_DIR = os.path.join(BASE_DIR, "..", "plotter", "charts")
CHART_FILE = os.path.join(CHARTS_DIR, "sound_chart.svg")

def generate_sound_chart():
    if not os.path.exists(DATA_FILE):
        print(f"Error: Sound log not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)

    times = []
    rms_values = []
    db_values = []

    try:
        with open(DATA_FILE, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception as e:
        print(f"Error reading data file: {e}", file=sys.stderr)
        sys.exit(2)

    if len(lines) < 2:
        print("No sound data to plot (or only header found).", file=sys.stderr)
        sys.exit(2)

    # Parse CSV (timestamp,rms,db)
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) >= 3:
            try:
                # Match logger format: "YYYY-MM-DD HH:MM:SS"
                ts = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
                rms = float(parts[1])
                db = float(parts[2]) if parts[2] not in ("", "None") else None

                times.append(ts)
                rms_values.append(rms)
                db_values.append(db)
            except ValueError:
                # Skip malformed lines
                continue

    if not rms_values:
        print("No valid numerical data to plot.", file=sys.stderr)
        sys.exit(2)

    os.makedirs(CHARTS_DIR, exist_ok=True)

    # --- Plotting ---
    plt.style.use("ggplot")
    plt.rcParams.update({'font.size': 12, 'axes.labelsize': 14, 'axes.titlesize': 16})
    fig, ax1 = plt.subplots(figsize=(12,6))

    # Plot RMS voltage
    ax1.plot(times, rms_values, color="blue", linewidth=1.5, label="RMS Voltage (V)")
    ax1.set_ylabel("RMS Voltage (V)", color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")

    # Secondary axis for dB SPL
    ax2 = ax1.twinx()
    ax2.plot(times, db_values, color="red", linewidth=1.5, label="dB SPL")
    ax2.set_ylabel("Sound Level (dB SPL)", color="red")
    ax2.tick_params(axis='y', labelcolor="red")

    # Title with duration
    duration_s = (times[-1] - times[0]).total_seconds()
    total_minutes = int(duration_s // 60)
    total_seconds = int(duration_s % 60)
    duration_str = f"{total_minutes:02d}m {total_seconds:02d}s"

    ax1.set_title(f"Sound RMS & dB SPL Timeline | Duration: {duration_str}")
    ax1.set_xlabel("Time (YYYY-MM-DD HH:MM:SS)")

    fig.autofmt_xdate()  # rotate timestamps for readability
    fig.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart generated: {CHART_FILE} with {len(rms_values)} data points.")

if __name__ == "__main__":
    generate_sound_chart()
