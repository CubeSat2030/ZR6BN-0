import os, sys
import matplotlib.pyplot as plt
import numpy as np

# --- Paths ---
# PATCH 1: Corrected file name to match the logger output
DATA_DIR = os.path.join("src", "logger", "data")
DATA_FILE = os.path.join(DATA_DIR, "sound_data_D0.txt") 
CHARTS_DIR = "src/plotter/charts"
CHART_FILE = os.path.join(CHARTS_DIR, "sound_chart.svg")

def generate_sound_chart():
    if not os.path.exists(DATA_FILE):
        print(f"Error: Sound log not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)

    uptime_seconds = []
    sound_levels = []

    try:
        with open(DATA_FILE, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception as e:
        print(f"Error reading data file: {e}", file=sys.stderr)
        sys.exit(2)

    if len(lines) < 2: 
        print("No sound data to plot (or only header found).", file=sys.stderr)
        sys.exit(2)

    # PATCH 2 & 3: Skip header and extract the correct columns
    # We use system_uptime_s (index 1) for X and sound_detected (index 2) for Y
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) >= 3: 
            try:
                # X-Axis: system_uptime_s (index 1)
                uptime = float(parts[1])
                # Y-Axis: sound_detected (index 2)
                sound_level = float(parts[2]) 

                uptime_seconds.append(uptime)
                sound_levels.append(sound_level)
            except ValueError:
                # Skip corrupted lines
                continue

    if not uptime_seconds:
        print("No valid numerical data to plot.", file=sys.stderr)
        sys.exit(2)

    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    # --- Plotting ---
    plt.style.use("ggplot")
    plt.rcParams.update({'font.size': 12, 'axes.labelsize': 14, 'axes.titlesize': 16})
    fig, ax = plt.subplots(figsize=(12,6))
    
    # Use a step plot for binary 0/1 data
    ax.step(uptime_seconds, sound_levels, where='post', color="purple", linewidth=1.5, label='Sound Detected (D0 Pin)')
    
    # Calculate duration for the title
    duration_s = uptime_seconds[-1] - uptime_seconds[0]
    total_minutes = int(duration_s // 60)
    total_seconds = int(duration_s % 60)
    duration_str = f"{total_minutes:02d}m {total_seconds:02d}s"

    ax.set_title(f"Sound Detection Timeline | Duration: {duration_str}")
    ax.set_xlabel("System Uptime (Seconds)")
    ax.set_ylabel("Detection State (1=Sound, 0=Quiet)")
    
    # Improve Y-axis readability for a binary plot
    ax.set_yticks([0, 1])
    ax.set_ylim(-0.1, 1.1)
    
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart generated: {CHART_FILE} with {len(uptime_seconds)} data points.")

if __name__ == "__main__":
    generate_sound_chart()

