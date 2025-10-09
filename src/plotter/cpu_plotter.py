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

DATA_DIR = "src/logger/data"
DATA_FILE = os.path.join(DATA_DIR, "CPU_TEMP.txt")
CHARTS_DIR = "src/plotter/charts"
CHART_FILE = os.path.join(CHARTS_DIR, "cpu_chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "cpu_chart_backup.svg")

def generate_chart():
    dates, temps = [], []

    if not os.path.exists(DATA_FILE):
        print(f"Error: Mission data file not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
            if lines and "timestamp" in lines[0]:
                lines = lines[1:]
            for line in lines:
                try:
                    timestamp_str, temp_str = line.strip().split(',')

                    # --- Robust Timestamp Parsing ---
                    try:
                        dt_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        time_obj = datetime.strptime(timestamp_str, "%H:%M:%S")
                        dt_obj = datetime.combine(datetime.now().date(), time_obj.time())

                    dates.append(dt_obj)
                    temps.append(float(temp_str))
                except (ValueError, IndexError):
                    continue
    except Exception as e:
        print(f"Error reading data file: {e}", file=sys.stderr)
        sys.exit(2)

    if not dates:
        print("No data to plot.", file=sys.stderr)
        sys.exit(2)

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

    if os.path.exists(CHART_FILE):
        os.replace(CHART_FILE, CHART_BACKUP_FILE)

    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart generated: {CHART_FILE} with {len(dates)} points over {duration_str}")

if __name__ == "__main__":
    generate_chart()
