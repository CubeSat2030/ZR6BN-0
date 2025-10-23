#!/usr/bin/env python3
"""
payload_flight_simulation_visual_flat.py
Flat / cinematic BACAR-13 visual export (one frame per telemetry row).
Left: vertical stylized rod + pale-lilac payload box (altitude-scaled).
Right: embedded mpu_chart.svg if present (flat).
Output: FullHD MP4 (exact telemetry duration).
"""

import os, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.patches import Rectangle
from PIL import Image
import warnings

# ---------------- CONFIG ----------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "MPU6050.txt")
CHART_SVG = os.path.join(PROJECT_ROOT, "plotter", "charts", "mpu_chart.svg")
OUT_DIR = os.path.join(PROJECT_ROOT, "simulation", "output")
OUT_FILE = os.path.join(OUT_DIR, "BACAR13_simulation_flat.mp4")

FRAME_W = 1920
FRAME_H = 1080
DPI = 150
CODEC = "libx264"

CUBE_COLOR = "#C8B9FF"  # pale lilac
ROD_COLOR = "#101217"   # near-black rod
PAST_COLOR = (1.0, 1.0, 1.0, 0.18)
FUTURE_COLOR = (0.6, 0.8, 1.0, 0.18)
LABEL_COLOR = "white"

MAX_ALT_KNOWN = 32000.0  # 32 km burst altitude (user-confirmed)

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
def altitude_to_color(h):
    """
    Map altitude (meters) to a cinematic background RGB tuple.
    Lower alt -> slightly warmer/darker; high alt -> near-space navy.
    """
    a = np.clip(h / MAX_ALT_KNOWN, 0.0, 1.0)
    if a < 0.25:
        t = a / 0.25
        base = np.array([0.02, 0.02, 0.04])
        sky  = np.array([0.08, 0.10, 0.20])
    elif a < 0.75:
        t = (a - 0.25) / 0.5
        base = np.array([0.08, 0.10, 0.20])
        sky  = np.array([0.03, 0.06, 0.14])
    else:
        t = (a - 0.75) / 0.25
        base = np.array([0.03, 0.06, 0.14])
        sky  = np.array([0.01, 0.02, 0.06])
    col = (1 - t) * base + t * sky
    return tuple(np.clip(col, 0, 1))

# ---------------- LOAD & PREP DATA ----------------
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"Telemetry file missing: {DATA_FILE}")

df = pd.read_csv(DATA_FILE, comment="#")
if "timestamp" not in df.columns:
    raise ValueError("MPU6050.txt must contain 'timestamp' column")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)
df = df.sort_values("timestamp").reset_index(drop=True)

# ensure numeric columns exist (safe fallback)
for c in ("velocity_m_s","accel_x_m_s2","accel_y_m_s2","accel_z_m_s2","altitude_m"):
    if c not in df.columns:
        df[c] = np.nan

# interpolate numeric where possible
numcols = df.select_dtypes(include=[np.number]).columns
df[numcols] = df[numcols].interpolate().fillna(np.nan)

# times (seconds since start)
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
if np.any(dt <= 0):
    pos = dt[dt > 0]
    dt[dt <= 0] = np.mean(pos) if len(pos) else 1.0

# ---------------- ALTITUDE (use altitude column or integrate velocity or synthesize) ----------------
if not df["altitude_m"].isna().all():
    alt = df["altitude_m"].to_numpy(dtype=float)
    print("Using altitude_m column from telemetry.")
elif not df["velocity_m_s"].isna().all():
    print("Integrating velocity_m_s -> altitude_m")
    vel = df["velocity_m_s"].to_numpy(dtype=float)
    alt = np.zeros(len(df))
    for i in range(1, len(df)):
        alt[i] = alt[i-1] + vel[i] * dt[i]
    alt = np.clip(alt, 0.0, MAX_ALT_KNOWN * 1.1)
else:
    # synthesize a realistic ascent -> burst -> descent profile
    print("No altitude or velocity present. Synthesizing altitude profile (burst at ~32km).")
    accel_present = not df[["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].isna().all().all()
    burst_index = None
    if accel_present:
        ax = df["accel_x_m_s2"].fillna(0).to_numpy()
        ay = df["accel_y_m_s2"].fillna(0).to_numpy()
        az = df["accel_z_m_s2"].fillna(0).to_numpy()
        mag = np.sqrt(ax*ax + ay*ay + az*az)
        burst_index = int(np.argmax(mag))
        if mag[burst_index] < np.median(mag) * 3:
            burst_index = None
    if burst_index is None:
        burst_index = len(df)//2
    climb_len = burst_index
    descent_len = len(df) - burst_index
    climb = np.linspace(0.0, MAX_ALT_KNOWN, climb_len, endpoint=False) if climb_len>0 else np.array([])
    descent = np.linspace(MAX_ALT_KNOWN, 0.0, descent_len) if descent_len>0 else np.array([])
    alt = np.concatenate([climb, descent])
    if len(alt) < len(df):
        alt = np.pad(alt, (0, len(df)-len(alt)), 'edge')
    elif len(alt) > len(df):
        alt = alt[:len(df)]

alt = np.clip(alt, 0.0, MAX_ALT_KNOWN * 1.05)

# ---------------- EVENT DETECTION (build event_windows BEFORE use) ----------------
# Use acceleration magnitude to detect burst and impact windows.
ax_col = df["accel_x_m_s2"].fillna(0).to_numpy()
ay_col = df["accel_y_m_s2"].fillna(0).to_numpy()
az_col = df["accel_z_m_s2"].fillna(0).to_numpy()
acc_mag = np.sqrt(ax_col*ax_col + ay_col*ay_col + az_col*az_col)

if len(acc_mag) == 0:
    # fallback: define simple windows
    burst_idx = len(df)//3
    impact_idx = int(len(df)*0.9)
else:
    burst_idx = int(np.argmax(acc_mag))
    tail_start = int(len(acc_mag) * 0.90)
    if tail_start < len(acc_mag):
        impact_idx = tail_start + int(np.argmax(acc_mag[tail_start:]))
    else:
        impact_idx = len(acc_mag) - 1

descent_start_idx = min(len(df)-1, burst_idx + 1)

event_windows = {
    "ASCENT": (0, max(0, burst_idx-1)),
    "BURST": (max(0, burst_idx-2), min(len(df)-1, burst_idx+4)),
    "DESCENT": (descent_start_idx, max(descent_start_idx+1, impact_idx-1)),
    "IMPACT": (max(0, impact_idx-3), min(len(df)-1, impact_idx+4))
}

# ---------------- EXPORT FPS (exact mapping: one frame per telemetry row) ----------------
median_dt = np.median(dt[np.where(dt>0)]) if np.any(dt>0) else 1.0
telemetry_rate = 1.0 / median_dt if median_dt > 0 else 1.0
export_fps = int(max(1, round(telemetry_rate)))
if export_fps > 60:
    warnings.warn(f"Telemetry rate {telemetry_rate:.2f}Hz > 60Hz; capping export FPS to 60 for encoder stability.")
    export_fps = 60

frames = len(df)
print(f"Telemetry rows: {len(df)}, median dt={median_dt:.3f}s, export_fps={export_fps}, frames={frames}")

# ---------------- LAYOUT parameters (2D flat cinematic) ----------------
left_w = 0.65
right_w = 1.0 - left_w
pad = 0.04

rod_x = 0.35  # fraction across left panel (0..1 within left)
rod_top = 0.88
rod_bottom = 0.12

def alt_to_yp(alt_m):
    t = np.clip(alt_m / MAX_ALT_KNOWN, 0.0, 1.0)
    return rod_bottom + (rod_top - rod_bottom) * t

# ---------------- FIGURE & STATIC ASSETS ----------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(FRAME_W / DPI, FRAME_H / DPI), dpi=DPI)
ax_left = fig.add_axes([0.0 + pad, 0.0 + pad, left_w - 2*pad, 1.0 - 2*pad])
ax_right = fig.add_axes([left_w + pad, 0.0 + pad, right_w - 2*pad, 1.0 - 2*pad])

ax_left.set_xlim(0,1); ax_left.set_ylim(0,1)
ax_left.axis("off")
ax_right.axis("off")

# load right chart image if available (Pillow)
chart_img = None
if os.path.exists(CHART_SVG):
    try:
        chart_img = Image.open(CHART_SVG).convert("RGBA")
    except Exception:
        chart_img = None

if chart_img is not None:
    ax_right.imshow(chart_img)
else:
    ax_right.set_facecolor("#0F0F0F")
    ax_right.text(0.5, 0.5, "mpu_chart.svg\nnot found", ha="center", va="center", color="white", fontsize=18)

# rod rectangle
rod_pixel_x = rod_x
rod_width = 0.015
rod = plt.Rectangle((rod_pixel_x - rod_width/2, rod_bottom - 0.02), rod_width, rod_top - rod_bottom + 0.04,
                    color=ROD_COLOR, zorder=1, alpha=0.95)
ax_left.add_patch(rod)

# faint ticks
n_ticks = 36
tick_ys = np.linspace(rod_bottom, rod_top, n_ticks)
for ty in tick_ys:
    ax_left.plot([rod_pixel_x], [ty], marker='o', markersize=4, color=(1,1,1,0.03))

# overlay labels & arrows (persistent)
overlay_ax = fig.add_axes([0,0,1,1], zorder=20)
overlay_ax.axis("off")
overlay_ax.text(0.04, 0.72, "future\nvertical\npayload\ntrajectory", fontsize=26, color=LABEL_COLOR, va="center")
overlay_ax.text(0.04, 0.45, "payload", fontsize=28, color=LABEL_COLOR, va="center")
overlay_ax.text(0.04, 0.22, "passed\nvertical\npayload\ntrajectory", fontsize=26, color=LABEL_COLOR, va="center")
overlay_ax.annotate("", xy=(0.45, 0.75), xytext=(0.15, 0.75),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color=LABEL_COLOR))
overlay_ax.annotate("", xy=(0.60, 0.52), xytext=(0.15, 0.52),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color=LABEL_COLOR))
overlay_ax.annotate("", xy=(0.40, 0.28), xytext=(0.15, 0.28),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color=LABEL_COLOR))

# dynamic artists
past_scatter = ax_left.scatter([], [], s=18, color=PAST_COLOR, zorder=5)
future_scatter = ax_left.scatter([], [], s=18, color=FUTURE_COLOR, zorder=4)
cube_size_frac = 0.08
cube_artist = Rectangle((rod_pixel_x - cube_size_frac/2, 0.5 - cube_size_frac/2), cube_size_frac, cube_size_frac,
                        facecolor=CUBE_COLOR, edgecolor="#2b2430", linewidth=1.0, zorder=10)
ax_left.add_patch(cube_artist)

ax_left.plot([rod_pixel_x], [rod_bottom], marker='s', markersize=6, color=(0.9,0.9,0.9,0.7), zorder=6)

# ---------------- EXPORT ----------------
writer = FFMpegWriter(fps=export_fps, metadata=dict(artist="BACAR-13 Replay"), codec=CODEC)
print(f"Exporting to: {OUT_FILE}\nframes={frames}, fps={export_fps}")

with writer.saving(fig, OUT_FILE, dpi=DPI):
    for i in range(frames):
        # dynamic background
        bg = altitude_to_color(alt[i])
        fig.patch.set_facecolor(bg)
        ax_left.set_facecolor(bg)

        # cube position
        y = alt_to_yp(alt[i])
        cube_artist.set_xy((rod_pixel_x - cube_size_frac/2, y - cube_size_frac/2))
        cube_artist.set_width(cube_size_frac)
        cube_artist.set_height(cube_size_frac)
        # subtle shade
        shade_factor = 0.12 * (1.0 - np.clip(alt[i] / MAX_ALT_KNOWN, 0.0, 1.0))
        facecol = tuple(np.clip(np.array((200/255.,185/255.,1.0)) - shade_factor, 0, 1))
        cube_artist.set_facecolor(facecol)

        # past/future dots
        past_idx = np.arange(0, i+1)
        future_idx = np.arange(i+1, frames)
        past_ys = alt_to_yp(alt[past_idx]) if len(past_idx)>0 else np.array([])
        future_ys = alt_to_yp(alt[future_idx]) if len(future_idx)>0 else np.array([])

        if len(past_ys)>0:
            past_xs = np.full_like(past_ys, rod_pixel_x)
            past_scatter.set_offsets(np.column_stack([past_xs, past_ys]))
            alphas = np.linspace(0.05, 0.35, len(past_ys))
            past_scatter.set_color([(1,1,1,a) for a in alphas])
        else:
            past_scatter.set_offsets([])

        if len(future_ys)>0:
            future_xs = np.full_like(future_ys, rod_pixel_x)
            step = max(1, len(future_ys)//36)
            sel = np.arange(0, len(future_ys), step)
            future_scatter.set_offsets(np.column_stack([future_xs[sel], future_ys[sel]]))
            alphas_f = np.linspace(0.12, 0.35, len(sel))
            future_scatter.set_color([(0.6,0.8,1.0,a) for a in alphas_f])
        else:
            future_scatter.set_offsets([])

        # halo glow when low
        halo = None
        if alt[i] < 12000:
            glow_strength = np.clip((12000.0 - alt[i]) / 12000.0, 0.0, 1.0)
            halo = ax_left.scatter([rod_pixel_x], [y - cube_size_frac*0.04], s=600*glow_strength,
                                   color=(1.0,0.95,0.6,0.06+0.18*glow_strength), zorder=6)

        # event banner texts
        fig.texts.clear()
        for name, (sidx, eidx) in event_windows.items():
            if sidx <= i <= eidx:
                center = (sidx + eidx) / 2.0
                dist = abs(i - center) / max(1.0, (eidx - sidx) / 2.0)
                alpha = np.clip(1.0 - dist, 0.25, 1.0)
                fig.text(0.03, 0.94, name, fontsize=20, color=(1,0.95,0.85,alpha),
                         bbox=dict(boxstyle="round,pad=0.4", facecolor=(0,0,0,0.6*alpha)))

        # timestamp HUD (small)
        ts = df["timestamp"].iloc[i].strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.70, 0.03, f"t={ts} | Alt={alt[i]:.0f} m", fontsize=10, color="white")

        writer.grab_frame(facecolor=fig.get_facecolor())

print("Export complete ->", OUT_FILE)
