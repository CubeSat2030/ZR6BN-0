import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.signal import savgol_filter

# =========================================================================
# Paths
# =========================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_FILE = os.path.join(PROJECT_ROOT, "src/logger/data/MPU6050.txt")
CHARTS_DIR = os.path.join(PROJECT_ROOT, "src/plotter/charts")
CHART_FILE = os.path.join(CHARTS_DIR, "mpu_chart.svg")

os.makedirs(CHARTS_DIR, exist_ok=True)

WINDOW_LENGTH = 51
POLY_ORDER = 3

HEADER_MAP = {
    "accel_x_g": "accel_x", "accel_y_g": "accel_y", "accel_z_g": "accel_z",
    "gyro_x_dps": "gyro_x", "gyro_y_dps": "gyro_y", "gyro_z_dps": "gyro_z",
    "ax": "accel_x", "ay": "accel_y", "az": "accel_z",
    "gx": "gyro_x", "gy": "gyro_y", "gz": "gyro_z",
}

# =========================================================================
# Flight phase time windows (local time)
# =========================================================================
T_ASCENT_START = datetime(2025,10,11,8,0,0)
T_BURST_START  = datetime(2025,10,11,10,29,50)
T_BURST_END    = datetime(2025,10,11,10,30,10)
T_DESCENT_END  = datetime(2025,10,11,10,39,0)
T_IMPACT_END   = datetime(2025,10,11,10,39,20)
T_END          = datetime(2025,10,11,11,0,0)

PHASES = [
    ("ASCENT",  T_ASCENT_START, T_BURST_START),
    ("BURST",   T_BURST_START,  T_BURST_END),
    ("DESCENT", T_BURST_END,    T_DESCENT_END),
    ("IMPACT",  T_DESCENT_END,  T_IMPACT_END),
]

# =========================================================================
# Read data
# =========================================================================
with open(DATA_FILE, "r") as f:
    lines = [ln for ln in f if not ln.startswith("#")]
header = [h.strip() for h in lines[0].split(",")]
raw_keys = header[1:]
internal_keys = [(k.strip(), HEADER_MAP.get(k.strip())) for k in raw_keys]
dates, data = [], {k: [] for k in ["accel_x","accel_y","accel_z","gyro_x","gyro_y","gyro_z"]}

for line in lines[1:]:
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < len(header): continue
    try:
        try: dt = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S.%f")
        except ValueError: dt = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        dates.append(dt)
    except: continue
    for i,(raw_k,internal_k) in enumerate(internal_keys):
        if internal_k is None: continue
        try: val = float(parts[i+1])
        except: val = np.nan
        data[internal_k].append(val)

dates = np.array(dates)
data = {k: np.array(v, dtype=float) for k,v in data.items()}

def smooth(y):
    if len(y) < WINDOW_LENGTH: return y
    return savgol_filter(y, WINDOW_LENGTH, POLY_ORDER)

# =========================================================================
# Plot setup
# =========================================================================
FIGURE_BG = '#0F0F0F'
AXES_BG   = '#1A1A1A'
TEXT_COLOR= '#F0F0F0'
BORDER_COLOR='#404040'
GRID_COLOR = '#2A2A2A'
ZERO_LINE  = '#888888'
colors = {"x": "#EF5350", "y": "#66BB6A", "z": "#42A5F5"}

plt.style.use("default")
plt.rcParams.update({
    "figure.facecolor": FIGURE_BG,
    "axes.facecolor": AXES_BG,
    "text.color": TEXT_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
})

fig, axes = plt.subplots(8, 1, figsize=(14, 24))
plt.subplots_adjust(hspace=0.35)

date_formatter = mdates.DateFormatter("%H:%M:%S")

# =========================================================================
# Draw each phase
# =========================================================================
for idx, (label, t_start, t_end) in enumerate(PHASES):
    # slice indices
    mask = (dates >= t_start) & (dates <= t_end)
    if not np.any(mask): continue

    # acceleration subplot
    ax_a = axes[idx*2]
    ax_a.set_title(f"{label} – Acceleration (Linear G-Forces)", fontsize=13)
    ax_a.set_ylabel("g")
    ax_a.axhline(0, color=ZERO_LINE, linestyle="--", linewidth=1.0)
    accel_data = np.concatenate([data[f"accel_{a}"][mask] for a in "xyz"])
    if np.all(np.isnan(accel_data)): continue
    y_lim = np.nanmax(np.abs(accel_data)) * 1.2
    ax_a.set_ylim(-y_lim, y_lim)
    for axis in "xyz":
        raw = data[f"accel_{axis}"][mask]
        ax_a.plot(dates[mask], raw, color=colors[axis], linewidth=0.6, alpha=0.1)
        ax_a.plot(dates[mask], smooth(raw), color=colors[axis], linewidth=1.8, label=f"A{axis.upper()}")
    g_net = np.sqrt(np.square(data["accel_x"][mask]) +
                    np.square(data["accel_y"][mask]) +
                    np.square(data["accel_z"][mask]))
    ax_a.plot(dates[mask], g_net, color="#FFD54F", linewidth=1.2, label="|a| total")
    ax_a.legend(loc="upper right", facecolor=AXES_BG, frameon=True, edgecolor=BORDER_COLOR)
    ax_a.xaxis.set_major_formatter(date_formatter)

    # gyro subplot
    ax_g = axes[idx*2+1]
    ax_g.set_title(f"{label} – Gyroscope (Rotational Velocity)", fontsize=13)
    ax_g.set_ylabel("°/s")
    gyro_data = np.concatenate([data[f"gyro_{a}"][mask] for a in "xyz"])
    g_lim = np.nanmax(np.abs(gyro_data)) * 1.2
    ax_g.set_ylim(-g_lim, g_lim)
    for axis in "xyz":
        raw = data[f"gyro_{axis}"][mask]
        ax_g.plot(dates[mask], raw, color=colors[axis], linewidth=0.6, alpha=0.1)
        ax_g.plot(dates[mask], smooth(raw), color=colors[axis], linewidth=1.8, label=f"G{axis.upper()}")
    ax_g.legend(loc="upper right", facecolor=AXES_BG, frameon=True, edgecolor=BORDER_COLOR)
    ax_g.xaxis.set_major_formatter(date_formatter)
    ax_g.set_xlabel("Time (HH:MM:SS)")

# =========================================================================
# Save
# =========================================================================
fig.suptitle("Kabot I Mission – MPU-6050 Detailed Flight Phases", fontsize=18, color=TEXT_COLOR)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(CHART_FILE)
plt.close(fig)

print(f"\n✅ Multi-phase chart saved to: {CHART_FILE}")
