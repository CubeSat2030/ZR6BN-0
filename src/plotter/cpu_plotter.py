import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os, sys

# Optional smoothing filter
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
DATA_FILE = os.path.join(PROJECT_ROOT, DATA_DIR_RELATIVE, "CPU_TEMP.txt")
CHARTS_DIR = os.path.join(PROJECT_ROOT, CHARTS_DIR_RELATIVE)
CHART_FILE = os.path.join(CHARTS_DIR, "cpu_chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "cpu_chart_backup.svg")

# =========================================================================
# The rest of the script is unchanged, utilizing the new absolute paths.
# =========================================================================

def generate_chart():
    dates, temps = [], []

    if not os.path.exists(DATA_FILE):
        # The error message now displays the absolute path for easier debugging
        print(f"Error: Mission data file not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
            if lines and "timestamp" in lines[0]:
                lines = lines[1:]
            for line in lines:
                try:
                    # FIX: The data has 3 fields (timestamp, temp, humidity), but we only need two.
                    # We unpack to three variables, using '_' for the unwanted humidity field.
                    timestamp_full_str, temp_str, _ = line.strip().split(',')
                    
                    # FIX: The timestamp includes fractional seconds (e.g., 08:00:00.000000000), 
                    # which breaks the original parsing. We strip the fractional part.
                    timestamp_str = timestamp_full_str.split('.')[0]
                    
                    # --- Robust Timestamp Parsing ---
                    dt_obj = None
                    try:
                        # Attempt to parse with date (original logic)
                        dt_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # Fallback for time-only format (matches the provided data)
                        time_obj = datetime.strptime(timestamp_str, "%H:%M:%S")
                        # Combine the time with today's date
                        dt_obj = datetime.combine(datetime.now().date(), time_obj.time())

                    dates.append(dt_obj)
                    temps.append(float(temp_str))
                except Exception: # Catch errors from split/unpack/conversion
                    continue
    except Exception as e:
        print(f"Error reading data file: {e}", file=sys.stderr)
        sys.exit(2)

    if not dates:
        print("No data to plot.", file=sys.stderr)
        sys.exit(2)

    # Use the now-absolute CHARTS_DIR
    os.makedirs(CHARTS_DIR, exist_ok=True)

    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 12, 'axes.labelsize': 14, 'axes.titlesize': 16})
    fig, ax = plt.subplots(figsize=(12, 7))

    start_time, end_time = dates[0], dates[-1]
    duration = end_time - start_time
    duration_str = f"{int(duration.total_seconds()//3600):02d}h {(int(duration.total_seconds())%3600)//60:02d}m {int(duration.total_seconds()%60):02d}s"

    ax.set_title(
        f"Kabot I CPU Temperature | Duration: {duration_str}\n"
        f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} | End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    ax.set_xlabel('Time')
    ax.set_ylabel('CPU Temp (°C)', color='tab:red')
    ax.plot(dates, temps, color='tab:red', linewidth=1.2, alpha=0.8, label='CPU Temp (Raw)')
    if HAS_SAVGOL and len(temps) >= 11:
        temp_smooth = savgol_filter(temps, 11, 3)
        ax.plot(dates, temp_smooth, color='darkred', linestyle='--', linewidth=2, label='Smoothed CPU Temp')
    ax.tick_params(axis='y', labelcolor='tab:red')

    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate(rotation=45)

    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    ax.legend(loc='upper left')

    # Use the now-absolute CHART_FILE and CHART_BACKUP_FILE
    if os.path.exists(CHART_FILE):
        os.replace(CHART_FILE, CHART_BACKUP_FILE)

    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart generated: {CHART_FILE} with {len(dates)} points over {duration_str}")

if __name__ == "__main__":
    generate_chart()
