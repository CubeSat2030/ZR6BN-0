import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import os, sys

# Try to import smoothing filter
try:
    from scipy.signal import savgol_filter
    HAS_SAVGOL = True
except Exception:
    HAS_SAVGOL = False

DATA_DIR = "src/logger/data"
DATA_FILE = os.path.join(DATA_DIR, "DHT11.txt")
CHARTS_DIR = "src/plotter/charts"
CHART_FILE = os.path.join(CHARTS_DIR, "dht_chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "dht_chart_backup.svg")

def generate_chart():
    dates, temps, hums = [], [], []

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
                    timestamp_str, temp_str, hum_str = line.strip().split(',')
                    
                    # --- PATCH START: Robust Timestamp Parsing ---
                    dt_obj = None
                    # Attempt 1: Full timestamp format (e.g., "2025-01-01 15:30:00")
                    try:
                        dt_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # Attempt 2: Time-only format (e.g., "15:30:00")
                        # This assumes the data was recorded on the current day if the date is missing.
                        time_obj = datetime.strptime(timestamp_str, "%H:%M:%S")
                        # Combine the time with today's date for plotting context
                        dt_obj = datetime.combine(datetime.now().date(), time_obj.time())

                    dates.append(dt_obj)
                    # --- PATCH END ---

                    temps.append(float(temp_str))
                    hums.append(float(hum_str))
                except (ValueError, IndexError):
                    # Skip lines that are corrupted or don't match expected CSV format
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
    fig, ax1 = plt.subplots(figsize=(12, 7))

    start_time, end_time = dates[0], dates[-1]
    duration = end_time - start_time
    duration_str = f"{int(duration.total_seconds()//3600):02d}h {(int(duration.total_seconds())%3600)//60:02d}m {int(duration.total_seconds()%60):02d}s"

    ax1.set_title(
        f"Kabot I Mission Readings | Duration: {duration_str}\n"
        f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} | End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (°C)', color='tab:red')
    ax1.plot(dates, temps, color='tab:red', linewidth=1.2, alpha=0.8, label='Temperature (Raw)')
    if HAS_SAVGOL and len(temps) >= 11:
        temp_smooth = savgol_filter(temps, 11, 3)
        ax1.plot(dates, temp_smooth, color='darkred', linestyle='--', linewidth=2, label='Smoothed Temp')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax1.xaxis.set_minor_locator(mdates.MinuteLocator(interval=2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate(rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='tab:blue')
    ax2.plot(dates, hums, color='tab:blue', linewidth=1.2, alpha=0.8, label='Humidity (Raw)')
    if HAS_SAVGOL and len(hums) >= 11:
        hum_smooth = savgol_filter(hums, 11, 3)
        ax2.plot(dates, hum_smooth, color='darkblue', linestyle='--', linewidth=2, label='Smoothed Hum')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.set_ylim(0, 100)

    ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    if os.path.exists(CHART_FILE):
        os.replace(CHART_FILE, CHART_BACKUP_FILE)

    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart generated: {CHART_FILE} with {len(dates)} points over {duration_str}")

if __name__ == "__main__":
    generate_chart()

