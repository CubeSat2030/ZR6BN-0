import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Optional smoothing
try:
    from scipy.signal import savgol_filter
    HAS_SAVGOL = True
except Exception:
    HAS_SAVGOL = False

# =========================================================================
# Paths
# =========================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

DATA_DIR_RELATIVE = "src/logger/data"
CHARTS_DIR_RELATIVE = "src/plotter/charts"

DATA_FILE = os.path.join(PROJECT_ROOT, DATA_DIR_RELATIVE, "MPU6050.txt")
CHARTS_DIR = os.path.join(PROJECT_ROOT, CHARTS_DIR_RELATIVE)
CHART_FILE = os.path.join(CHARTS_DIR, "mpu_chart.svg")
CHART_BACKUP_FILE = os.path.join(CHARTS_DIR, "mpu_chart_backup.svg")

WINDOW_LENGTH = 51
POLY_ORDER = 3

HEADER_MAP = {
    "accel_x_g": "accel_x", "accel_y_g": "accel_y", "accel_z_g": "accel_z",
    "gyro_x_dps": "gyro_x", "gyro_y_dps": "gyro_y", "gyro_z_dps": "gyro_z",
    "ax": "accel_x", "ay": "accel_y", "az": "accel_z",
    "gx": "gyro_x", "gy": "gyro_y", "gz": "gyro_z",
}

def generate_mpu_chart():
    if not os.path.exists(DATA_FILE):
        print(f"Error: Mission data file not found at {DATA_FILE}", file=sys.stderr)
        sys.exit(2)

    # --- Read file while skipping comment lines (# headers) ---
    with open(DATA_FILE, "r") as f:
        lines = [ln for ln in f if not ln.startswith("#")]

    if not lines:
        print("Error: Log file is empty.", file=sys.stderr)
        sys.exit(2)

    header = [h.strip() for h in lines[0].split(",")]
    if len(header) < 7 or header[0].lower() != "timestamp":
        print("Error: Unexpected header format. First column must be 'timestamp'.", file=sys.stderr)
        print(f"Header read: {header}", file=sys.stderr)
        sys.exit(2)

    raw_keys = header[1:]
    internal_keys = []
    for k in raw_keys:
        ik = HEADER_MAP.get(k.strip())
        internal_keys.append((k.strip(), ik))

    dates = []
    data = {k: [] for k in ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]}

    # --- Parse rows ---
    for line in lines[1:]:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) < len(header):
            continue

        try:
            t = parts[0]
            try:
                dt_obj = datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                dt_obj = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            dates.append(dt_obj)
        except Exception:
            continue

        for i, (raw_k, internal_k) in enumerate(internal_keys):
            if internal_k is None:
                continue
            try:
                val = float(parts[i+1])
            except Exception:
                val = np.nan
            data[internal_k].append(val)

    if not dates or all(len(v) == 0 for v in data.values()):
        print("Error: No valid data parsed.", file=sys.stderr)
        sys.exit(2)

    os.makedirs(CHARTS_DIR, exist_ok=True)

    start_time, end_time = dates[0], dates[-1]
    duration = end_time - start_time
    total_hours = int(duration.total_seconds() // 3600)
    total_minutes = int((duration.total_seconds() % 3600) // 60)
    total_seconds = int(duration.total_seconds() % 60)
    duration_str = f"{total_hours:02d}h {total_minutes:02d}m {total_seconds:02d}s"

    # =======================
    # Plot style/theme
    # =======================
    FIGURE_BG = '#0F0F0F'
    AXES_BG = '#1A1A1A'
    TEXT_COLOR = '#F0F0F0'
    BORDER_COLOR = '#404040'
    GRID_COLOR = '#2A2A2A'
    ZERO_LINE_COLOR = '#888888'

    colors = {"x": "#EF5350", "y": "#66BB6A", "z": "#42A5F5"}

    plt.style.use("default")
    plt.rcParams.update({
        "font.size": 10,
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "text.color": TEXT_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "figure.facecolor": FIGURE_BG,
        "axes.facecolor": AXES_BG,
        "savefig.facecolor": FIGURE_BG,
        "grid.color": GRID_COLOR,
        "grid.linestyle": "-",
        "grid.alpha": 1.0,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.edgecolor": BORDER_COLOR,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
    })

    fig, (ax_accel, ax_gyro) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    plt.subplots_adjust(hspace=0.25)
    fig.set_facecolor(FIGURE_BG)
    ax_accel.set_facecolor(AXES_BG)
    ax_gyro.set_facecolor(AXES_BG)

    fig.suptitle(
        f"Kabot I Mission MPU-6050 Motion Analysis | Duration: {duration_str}\n"
        f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} | End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
        fontsize=16,
        color=TEXT_COLOR
    )

    date_formatter = mdates.DateFormatter("%H:%M")

    def maybe_smooth(series):
        if HAS_SAVGOL and len(series) >= WINDOW_LENGTH and WINDOW_LENGTH % 2 == 1:
            try:
                return savgol_filter(series, WINDOW_LENGTH, POLY_ORDER)
            except Exception:
                return None
        return None

    # ---- ACCELERATION ----
    ax_accel.set_title("Acceleration (Linear G-Forces)", fontsize=14)
    ax_accel.set_ylabel("Acceleration (g)")
    accel_data = np.concatenate([data[f"accel_{axis}"] for axis in ["x","y","z"]])
    y_limit = np.nanmax(np.abs(accel_data)) * 1.05
    ax_accel.set_ylim(-y_limit, y_limit)
    ax_accel.axhline(0, color=ZERO_LINE_COLOR, linestyle="--", linewidth=1.2, zorder=0)

    for axis in ["x","y","z"]:
        raw = np.array(data[f"accel_{axis}"], dtype=float)
        ax_accel.plot(dates, raw, color=colors[axis], linewidth=0.7, alpha=0.05)
        smooth = maybe_smooth(raw)
        if smooth is not None:
            ax_accel.plot(dates, smooth, color=colors[axis], linewidth=2.0, label=f"Accel {axis.upper()}")

    # --- Total linear g ---
    try:
        g_net = np.sqrt(
            np.square(data["accel_x"]) +
            np.square(data["accel_y"]) +
            np.square(data["accel_z"])
        )
        ax_accel.plot(
            dates, g_net, color="#FFD54F", linewidth=1.5,
            label="Net |a| (Total Linear G)"
        )
    except Exception as e:
        print(f"Warning: Could not compute total g magnitude: {e}", file=sys.stderr)

    # ---- BURST / IMPACT ----
    burst_time = datetime.strptime("2025-10-11 10:30:01.200", "%Y-%m-%d %H:%M:%S.%f")
    impact_time = datetime.strptime("2025-10-11 10:39:18.000", "%Y-%m-%d %H:%M:%S.%f")

    def mark_event(ax, dt, label, color="#FF8A65"):
        ax.axvline(dt, color=color, linestyle="--", linewidth=1.2, zorder=5)
        ax.text(
            dt, ax.get_ylim()[1]*0.9, label,
            rotation=90, va="top", ha="right",
            color=color, fontsize=9,
            bbox=dict(facecolor='black', alpha=0.4, edgecolor='none')
        )

    mark_event(ax_accel, burst_time, "BURST (Balloon Rupture)", "#FF8A65")
    mark_event(ax_accel, impact_time, "IMPACT (Ground Contact)", "#FF5252")

    ax_accel.legend(loc="upper right", ncol=3, facecolor=AXES_BG, frameon=True,
                    edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR)
    ax_accel.spines['top'].set_visible(False)
    ax_accel.spines['right'].set_visible(False)

    # ---- GYRO ----
    ax_gyro.set_title("Gyroscope (Rotational Velocity)", fontsize=14)
    ax_gyro.set_xlabel("Time (HH:MM)")
    ax_gyro.set_ylabel("Angular Velocity (°/s)")
    gyro_data = np.concatenate([data[f"gyro_{axis}"] for axis in ["x","y","z"]])
    y_limit_g = np.nanmax(np.abs(gyro_data)) * 1.05
    ax_gyro.set_ylim(-y_limit_g, y_limit_g)
    ax_gyro.axhline(0, color=ZERO_LINE_COLOR, linestyle="--", linewidth=1.2, zorder=0)

    for axis in ["x","y","z"]:
        raw = np.array(data[f"gyro_{axis}"], dtype=float)
        ax_gyro.plot(dates, raw, color=colors[axis], linewidth=0.7, alpha=0.05)
        smooth = maybe_smooth(raw)
        if smooth is not None:
            ax_gyro.plot(dates, smooth, color=colors[axis], linewidth=2.0, label=f"Gyro {axis.upper()}")

    # --- Mark events on gyro plot too ---
    mark_event(ax_gyro, burst_time, "BURST (Balloon Rupture)", "#FF8A65")
    mark_event(ax_gyro, impact_time, "IMPACT (Ground Contact)", "#FF5252")

    ax_gyro.legend(loc="upper right", ncol=3, facecolor=AXES_BG, frameon=True,
                   edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR)
    ax_gyro.spines['top'].set_visible(False)
    ax_gyro.spines['right'].set_visible(False)
    ax_gyro.xaxis.set_major_formatter(date_formatter)

    fig.autofmt_xdate(rotation=45)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save chart
    try:
        if os.path.exists(CHART_FILE):
            os.replace(CHART_FILE, CHART_BACKUP_FILE)
        plt.savefig(CHART_FILE)
        plt.close(fig)
        print(f"\n✅ Generated MPU-6050 chart: {CHART_FILE}")
        print(f"Chart covers {len(dates)} points over {duration_str}.")
    except Exception as e:
        print(f"Error saving chart: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    generate_mpu_chart()
