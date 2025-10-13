import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Try to import SciPy smoothing; if unavailable, continue without it
try:
    from scipy.signal import savgol_filter
    HAS_SAVGOL = True
except Exception:
    HAS_SAVGOL = False

# =========================================================================
# FIX: Use absolute paths based on the script's location for robustness.
# =========================================================================

# Get the directory of the current script file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Assume the project root is two levels up from this script (plotter/generate_chart.py)
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR)) 

# Paths (relative to project root)
DATA_DIR_RELATIVE = "src/logger/data"
CHARTS_DIR_RELATIVE = "src/plotter/charts"

# Construct ABSOLUTE paths
DATA_FILE = os.path.join(PROJECT_ROOT, DATA_DIR_RELATIVE, "MPU6050.txt")
CHARTS_DIR = os.path.join(PROJECT_ROOT, CHARTS_DIR_RELATIVE)
CHART_FILE = os.path.join(CHARTS_DIR, "mpu_chart.svg")  # aligns with WebUI
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "mpu_chart_backup.svg")

# Smoothing settings (used only if HAS_SAVGOL and enough points)
WINDOW_LENGTH = 51  # must be odd and <= len(series)
POLY_ORDER = 3

# Map possible header names to internal keys
HEADER_MAP = {
    "accel_x": "accel_x", "accel_y": "accel_y", "accel_z": "accel_z",
    "gyro_x":  "gyro_x",  "gyro_y":  "gyro_y",  "gyro_z":  "gyro_z",
    "ax": "accel_x", "ay": "accel_y", "az": "accel_z",
    "gx": "gyro_x",  "gy": "gyro_y",  "gz": "gyro_z",
}

def generate_mpu_chart():
    # Basic checks
    if not os.path.exists(DATA_FILE):
        # Print the absolute path for the user's debug purposes
        print(f"Error: Mission data file not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)
# ... (rest of the code remains the same from here down) ...
    # Read file
    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading data file: {e}", file=sys.stderr)
        sys.exit(2)

    if not lines:
        print("Error: Log file is empty.", file=sys.stderr)
        sys.exit(2)

    # Parse header
    header = [h.strip() for h in lines[0].strip().split(",")]
    if len(header) < 7 or header[0].lower() != "timestamp":
        print("Error: Unexpected header format. First column must be 'timestamp'.", file=sys.stderr)
        print(f"Header read: {header}", file=sys.stderr)
        sys.exit(2)

    # Build key list using normalized names
    raw_keys = header[1:]
    internal_keys = []
    for k in raw_keys:
        ik = HEADER_MAP.get(k.strip())
        if ik:
            internal_keys.append((k.strip(), ik))
        else:
            # Unknown column; skip it gracefully
            internal_keys.append((k.strip(), None))

    # Prepare containers
    dates = []
    data = {
        "accel_x": [], "accel_y": [], "accel_z": [],
        "gyro_x":  [], "gyro_y":  [], "gyro_z":  []
    }

    # Parse rows
    for line in lines[1:]:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) < 7:
            continue
            
        # --- PATCH START: Robust Timestamp Parsing ---
        try:
            timestamp_str = parts[0]
            dt_obj = None
            
            # Attempt 1: Full timestamp format (e.g., "2025-01-01 15:30:00")
            try:
                dt_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Attempt 2: Time-only format (e.g., "15:30:00")
                time_obj = datetime.strptime(timestamp_str, "%H:%M:%S")
                # Combine the time with today's date for plotting context
                dt_obj = datetime.combine(datetime.now().date(), time_obj.time())
            
            dates.append(dt_obj)
        except Exception:
            # If parsing fails entirely, skip the line
            continue
        # --- PATCH END ---

        for i, (raw_k, internal_k) in enumerate(internal_keys):
            if internal_k is None:
                continue
            try:
                # Use i+1 because parts[0] is the timestamp
                val = float(parts[i+1])
            except Exception:
                val = np.nan
            data[internal_k].append(val)

    if not dates or all(len(v) == 0 for v in data.values()):
        print("Error: No data to plot.", file=sys.stderr)
        sys.exit(2)

    # Ensure charts dir
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # Duration
    start_time = dates[0]
    end_time = dates[-1]
    duration = end_time - start_time
    total_hours = int(duration.total_seconds() // 3600)
    total_minutes = int((duration.total_seconds() % 3600) // 60)
    total_seconds = int(duration.total_seconds() % 60)
    duration_str = f"{total_hours:02d}h {total_minutes:02d}m {total_seconds:02d}s"

    # ======================================================================
    # PROFESSIONAL DARK THEME CHANGES START HERE
    # ======================================================================

    # 1. Define Professional/Minimal Colors
    FIGURE_BG = '#0F0F0F'   # Near-black for a strong contrast border
    AXES_BG = '#1A1A1A'     # Plot area background (slight contrast to figure)
    TEXT_COLOR = '#F0F0F0'  # Bright white/light gray text
    BORDER_COLOR = '#404040' # Soft gray for axes and minor lines
    GRID_COLOR = '#2A2A2A'  # Subtle grid lines (darker than border)
    
    # 2. Refined Muted Color Palette (High contrast against the dark background)
    colors = {
        "x": "#EF5350", # Material Red (for X)
        "y": "#66BB6A", # Material Green (for Y)
        "z": "#42A5F5"  # Material Blue (for Z)
    }

    # 3. Apply Minimalist rcParams
    plt.style.use("default") 
    plt.rcParams.update({
        "font.size": 10, 
        "axes.labelsize": 12, 
        "axes.titlesize": 14,
        
        # Color settings
        "text.color": TEXT_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "figure.facecolor": FIGURE_BG,
        "axes.facecolor": AXES_BG,
        "savefig.facecolor": FIGURE_BG,
        
        # Grid settings (Minimalist: only horizontal grid lines)
        "grid.color": GRID_COLOR,
        "grid.linestyle": "-", 
        "grid.alpha": 1.0, # Full opacity for consistency
        "axes.grid": True, # Ensure grid is on
        "axes.grid.axis": "y", # Only show y-axis grid lines (more professional)
        
        # Axes line/tick settings (Thin, light lines)
        "axes.edgecolor": BORDER_COLOR,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
    })

    fig, (ax_accel, ax_gyro) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # Ensure background colors are set
    fig.set_facecolor(FIGURE_BG)
    ax_accel.set_facecolor(AXES_BG)
    ax_gyro.set_facecolor(AXES_BG)
    
    # Overall Title
    fig.suptitle(
        f"Kabot I Mission MPU-6050 Motion Analysis | Duration: {duration_str}\n"
        f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} | End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
        fontsize=16,
        color=TEXT_COLOR
    )

    date_formatter = mdates.DateFormatter("%H:%M")

    # Helper for smoothing
    def maybe_smooth(series):
        if not HAS_SAVGOL:
            return None
        n = len(series)
        if n < WINDOW_LENGTH or WINDOW_LENGTH % 2 == 0:
            return None
        try:
            return savgol_filter(series, WINDOW_LENGTH, POLY_ORDER)
        except Exception:
            return None

    # Accel Plot
    ax_accel.set_title("Acceleration Data (Linear G-Forces)", fontsize=14, color=TEXT_COLOR)
    ax_accel.set_ylabel("Acceleration (g)")
    for axis in ["x", "y", "z"]:
        raw = np.array(data[f"accel_{axis}"], dtype=float)
        # Raw data: Thinner line, lower opacity to push it to the background
        ax_accel.plot(dates, raw, label=f"Accel {axis} (Raw)", color=colors[axis], linewidth=0.7, alpha=0.10) 
        smooth = maybe_smooth(raw)
        if smooth is not None:
            # Smoothed data: Thicker line, full opacity, clearly showing the trend
            ax_accel.plot(dates, smooth, label=f"Accel {axis} (Smoothed)", color=colors[axis], linewidth=2.0) 

    # Clean up spines (the box around the plot)
    ax_accel.spines['top'].set_visible(False)
    ax_accel.spines['right'].set_visible(False)
    
    # Legend: Minimalist styling
    ax_accel.legend(loc="upper right", ncol=3, facecolor=AXES_BG, frameon=True, 
                    edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR)

    # Gyro Plot
    ax_gyro.set_title("Gyroscope Data (Rotational Velocity)", fontsize=14, color=TEXT_COLOR)
    ax_gyro.set_xlabel("Time (HH:MM)")
    ax_gyro.set_ylabel("Angular Velocity (deg/s)")
    for axis in ["x", "y", "z"]:
        raw = np.array(data[f"gyro_{axis}"], dtype=float)
        # Raw data: Thinner line, lower opacity
        ax_gyro.plot(dates, raw, label=f"Gyro {axis} (Raw)", color=colors[axis], linewidth=0.7, alpha=0.10)
        smooth = maybe_smooth(raw)
        if smooth is not None:
            # Smoothed data: Thicker line, full opacity
            ax_gyro.plot(dates, smooth, label=f"Gyro {axis} (Smoothed)", color=colors[axis], linewidth=2.0)

    ax_gyro.xaxis.set_major_formatter(date_formatter)
    
    # Clean up spines (the box around the plot)
    ax_gyro.spines['top'].set_visible(False)
    ax_gyro.spines['right'].set_visible(False)

    # Legend: Minimalist styling
    ax_gyro.legend(loc="upper right", ncol=3, facecolor=AXES_BG, frameon=True, 
                    edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR)

    fig.autofmt_xdate(rotation=45)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # ======================================================================
    # PROFESSIONAL DARK THEME CHANGES END HERE
    # ======================================================================

    # Backup + save
    try:
        if os.path.exists(CHART_FILE):
            os.replace(CHART_FILE, CHART_BACKUP_FILE)
        plt.savefig(CHART_FILE)
        plt.close(fig)
        print(f"\nSuccessfully generated MPU-6050 mission chart: '{CHART_FILE}'")
        print(f"Chart covers {len(dates)} points over {duration_str}.")
    except Exception as e:
        print(f"Error saving chart: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    generate_mpu_chart()
