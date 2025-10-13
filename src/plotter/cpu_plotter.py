import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os, sys
import numpy as np # Import numpy for data processing functions

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

    # Convert temps to numpy array for easier calculation
    temps_np = np.array(temps)
    
    # Ensure charts dir
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # ======================================================================
    # SCIENTIFIC/ACCURATE DARK THEME CHANGES START HERE
    # ======================================================================

    # 1. Define Professional/Minimal Colors
    FIGURE_BG = '#0F0F0F'   
    AXES_BG = '#1A1A1A'     
    TEXT_COLOR = '#F0F0F0'  
    BORDER_COLOR = '#404040' 
    GRID_COLOR = '#2A2A2A'  
    
    # 2. Primary data color (Warm orange/red is good for heat/temp)
    TEMP_COLOR = '#FF9800' # Muted Orange
    
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
        
        # Grid settings (Only horizontal grid lines for Y-axis reference)
        "grid.color": GRID_COLOR,
        "grid.linestyle": "-", 
        "grid.alpha": 1.0, 
        "axes.grid": True, 
        "axes.grid.axis": "y", 
        
        # Axes line/tick settings (Minimalist and thin)
        "axes.edgecolor": BORDER_COLOR,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
    })

    fig, ax = plt.subplots(figsize=(12, 7))

    start_time, end_time = dates[0], dates[-1]
    duration = end_time - start_time
    duration_str = f"{int(duration.total_seconds()//3600):02d}h {(int(duration.total_seconds())%3600)//60:02d}m {int(duration.total_seconds()%60):02d}s"

    # Set title with explicit color
    ax.set_title(
        f"Kabot I CPU Temperature Analysis | Duration: {duration_str}\n"
        f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} | End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
        color=TEXT_COLOR
    )

    ax.set_xlabel('Time')
    
    # Set Y-axis label with primary color
    ax.set_ylabel('CPU Temp (°C)', color=TEMP_COLOR)
    
    # Raw data: Very low opacity to show noise background
    ax.plot(dates, temps_np, color=TEMP_COLOR, linewidth=0.7, alpha=0.10, label='Raw Temp')
    
    if HAS_SAVGOL and len(temps_np) >= 11:
        # Smoothed data: Primary line, full opacity
        temp_smooth = savgol_filter(temps_np, 11, 3)
        ax.plot(dates, temp_smooth, color=TEMP_COLOR, linestyle='-', linewidth=2.5, label='Smoothed Trend')
        
    ax.tick_params(axis='y', labelcolor=TEMP_COLOR)

    # SCIENTIFIC ACCURACY: Add a marker for the average temperature (useful context)
    avg_temp = np.nanmean(temps_np)
    ax.axhline(avg_temp, color=TEMP_COLOR, linestyle=':', linewidth=1.0, alpha=0.7, label=f'Average Temp ({avg_temp:.1f}°C)')

    # SCIENTIFIC ACCURACY: Use ceiling and floor to ensure min/max are shown cleanly
    min_temp, max_temp = np.nanmin(temps_np), np.nanmax(temps_np)
    # Set Y-limit to show range clearly, plus a small buffer
    ax.set_ylim(np.floor(min_temp) - 2, np.ceil(max_temp) + 2) 

    # Clean up spines (the box around the plot)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Minor ticks only on Y-axis (less clutter)
    ax.yaxis.set_minor_locator(plt.MaxNLocator(20)) # Ensure dense ticks for accuracy
    ax.grid(True, axis='y', which='major', linestyle='-', linewidth=0.8, alpha=0.4, color=GRID_COLOR)
    ax.grid(True, axis='y', which='minor', linestyle=':', linewidth=0.4, alpha=0.2, color=GRID_COLOR)

    fig.autofmt_xdate(rotation=45)

    # Legend: Minimalist styling with professional color focus
    ax.legend(loc='upper left', facecolor=AXES_BG, frameon=True, 
              edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, title="Temperature Data")

    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust for suptitle
    
    # ======================================================================
    # SCIENTIFIC/ACCURATE DARK THEME CHANGES END HERE
    # ======================================================================

    # Use the now-absolute CHART_FILE and CHART_BACKUP_FILE
    if os.path.exists(CHART_FILE):
        os.replace(CHART_FILE, CHART_BACKUP_FILE)

    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart generated: {CHART_FILE} with {len(dates)} points over {duration_str}")

if __name__ == "__main__":
    generate_chart()
