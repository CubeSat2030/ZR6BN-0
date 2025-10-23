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

# ---------------- LOAD DATA ----------------
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
    # if outer values look wrong, clip
    alt = np.clip(alt, 0.0, MAX_ALT_KNOWN * 1.1)
else:
    # synthesize a realistic ascent -> burst -> descent profile
    print("No altitude or velocity present. Synthesizing altitude profile (burst at ~32km).")
    # detect burst by accel spike if available
    accel_present = not df[["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].isna().all().all()
    burst_index = None
    if accel_present:
        ax = df["accel_x_m_s2"].fillna(0).to_numpy()
        ay = df["accel_y_m_s2"].fillna(0).to_numpy()
        az = df["accel_z_m_s2"].fillna(0).to_numpy()
        mag = np.sqrt(ax*ax + ay*ay + az*az)
        burst_index = int(np.argmax(mag))
        # require a noticeable spike relative to median
        if mag[burst_index] < np.median(mag) * 3:
            burst_index = None
    if burst_index is None:
        # fallback: set burst near mid-sample
        burst_index = len(df)//2

    # create a smooth rise to MAX_ALT_KNOWN at burst_index then descend
    climb_len = burst_index
    descent_len = len(df) - burst_index
    climb = np.linspace(0.0, MAX_ALT_KNOWN, climb_len, endpoint=False) if climb_len>0 else np.array([])
    descent = np.linspace(MAX_ALT_KNOWN, 0.0, descent_len) if descent_len>0 else np.array([])
    alt = np.concatenate([climb, descent])
    # safety: if lengths differ cause final length mismatch, pad/trim
    if len(alt) < len(df):
        alt = np.pad(alt, (0, len(df)-len(alt)), 'edge')
    elif len(alt) > len(df):
        alt = alt[:len(df)]

# clamp alt to [0, MAX_ALT_KNOWN * 1.05]
alt = np.clip(alt, 0.0, MAX_ALT_KNOWN * 1.05)

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
# left panel portion (0.65 width)
left_w = 0.65
right_w = 1.0 - left_w
pad = 0.04

rod_x = 0.35  # fraction across left panel (0..1 within left)
rod_top = 0.88
rod_bottom = 0.12

# map altitude (0..MAX_ALT_KNOWN) -> y position within left panel (rod_top..rod_bottom)
def alt_to_yp(alt_m):
    t = np.clip(alt_m / MAX_ALT_KNOWN, 0.0, 1.0)
    return rod_bottom + (rod_top - rod_bottom) * (t)

# ---------------- FIGURE & STATIC ASSETS ----------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(FRAME_W / DPI, FRAME_H / DPI), dpi=DPI)
ax_left = fig.add_axes([0.0 + pad, 0.0 + pad, left_w - 2*pad, 1.0 - 2*pad])
ax_right = fig.add_axes([left_w + pad, 0.0 + pad, right_w - 2*pad, 1.0 - 2*pad])

ax_left.set_xlim(0,1); ax_left.set_ylim(0,1)
ax_left.axis("off")
ax_right.axis("off")

# prepare right chart image if available (no cairosvg dependency)
chart_img = None
if os.path.exists(CHART_SVG):
    try:
        # Pillow can open some SVG via its loader; if not, skip gracefully
        chart_img = Image.open(CHART_SVG).convert("RGBA")
    except Exception:
        chart_img = None

if chart_img is not None:
    ax_right.imshow(chart_img)
else:
    ax_right.set_facecolor("#0F0F0F")
    ax_right.text(0.5, 0.5, "mpu_chart.svg\nnot found", ha="center", va="center", color="white", fontsize=18)

# static left background gradient (we will set fig.patch each frame for dynamic color)
# draw the rod as a vertical soft rectangle (simulate tapered shadow)
rod_pixel_x = rod_x
rod_width = 0.015
rod = plt.Rectangle((rod_pixel_x - rod_width/2, rod_bottom - 0.02), rod_width, rod_top - rod_bottom + 0.04,
                    color=ROD_COLOR, zorder=1, alpha=0.95)
ax_left.add_patch(rod)

# draw tick dots positions along the rod for visual context (spaced)
n_ticks = 36
tick_ys = np.linspace(rod_bottom, rod_top, n_ticks)
for ty in tick_ys:
    ax_left.plot([rod_pixel_x], [ty], marker='o', markersize=4, color=(1,1,1,0.03))

# static left labels (positioned like your reference)
overlay_ax = fig.add_axes([0,0,1,1], zorder=20)
overlay_ax.axis("off")
overlay_ax.text(0.04, 0.72, "future\nvertical\npayload\ntrajectory", fontsize=26, color=LABEL_COLOR, va="center")
overlay_ax.text(0.04, 0.45, "payload", fontsize=28, color=LABEL_COLOR, va="center")
overlay_ax.text(0.04, 0.22, "passed\nvertical\npayload\ntrajectory", fontsize=26, color=LABEL_COLOR, va="center")

# arrows using overlay axis (axes fraction coords)
overlay_ax.annotate("", xy=(0.45, 0.75), xytext=(0.15, 0.75),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color=LABEL_COLOR))
overlay_ax.annotate("", xy=(0.60, 0.52), xytext=(0.15, 0.52),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color=LABEL_COLOR))
overlay_ax.annotate("", xy=(0.40, 0.28), xytext=(0.15, 0.28),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color=LABEL_COLOR))

# prepare artists for dynamic elements
past_scatter = ax_left.scatter([], [], s=18, color=PAST_COLOR, zorder=5)
future_scatter = ax_left.scatter([], [], s=18, color=FUTURE_COLOR, zorder=4)
cube_artist = Rectangle((rod_pixel_x - 0.04, 0.5 - 0.04), 0.08, 0.08,
                        facecolor=CUBE_COLOR, edgecolor="#2b2430", linewidth=1.0, zorder=10)
ax_left.add_patch(cube_artist)

# small ground marker at bottom
ax_left.plot([rod_pixel_x], [rod_bottom], marker='s', markersize=6, color=(0.9,0.9,0.9,0.7), zorder=6)

# ---------------- EXPORT (FFMpegWriter) ----------------
writer = FFMpegWriter(fps=export_fps, metadata=dict(artist="BACAR-13 Replay"), codec=CODEC)
print(f"Exporting to: {OUT_FILE}\nframes={frames}, fps={export_fps}")

# dynamic frame loop — one frame per telemetry row (exact mapping)
with writer.saving(fig, OUT_FILE, dpi=DPI):
    for i in range(frames):
        # set dynamic background color based on altitude
        bg = altitude_to_color(alt[i])
        fig.patch.set_facecolor(bg)
        ax_left.set_facecolor(bg)

        # compute cube center y in left panel coords
        y = alt_to_yp(alt[i])
        # convert fraction to axes units — our ax_left is 0..1
        cube_size_frac = 0.08
        cube_artist.set_xy((rod_pixel_x - cube_size_frac/2, y - cube_size_frac/2))
        cube_artist.set_width(cube_size_frac)
        cube_artist.set_height(cube_size_frac)
        # subtle shading: slightly darken cube when low alt
        shade_factor = 0.12 * (1.0 - np.clip(alt[i] / MAX_ALT_KNOWN, 0.0, 1.0))
        facecol = tuple(np.clip(np.array((200/255.,185/255.,1.0)) - shade_factor, 0, 1))
        cube_artist.set_facecolor(facecol)

        # past / future points along rod
        past_idx = np.arange(0, i+1)
        future_idx = np.arange(i+1, frames)
        past_ys = alt_to_yp(alt[past_idx]) if len(past_idx)>0 else np.array([])
        future_ys = alt_to_yp(alt[future_idx]) if len(future_idx)>0 else np.array([])

        # plot small faded dots for passed and future
        if len(past_ys)>0:
            past_xs = np.full_like(past_ys, rod_pixel_x)
            past_scatter.set_offsets(np.column_stack([past_xs, past_ys]))
            # progressively fade older points
            alphas = np.linspace(0.05, 0.35, len(past_ys))
            past_scatter.set_color([(1,1,1,a) for a in alphas])
        else:
            past_scatter.set_offsets([])

        if len(future_ys)>0:
            future_xs = np.full_like(future_ys, rod_pixel_x)
            # draw fewer future dots if too many
            step = max(1, len(future_ys)//36)
            sel = np.arange(0, len(future_ys), step)
            future_scatter.set_offsets(np.column_stack([future_xs[sel], future_ys[sel]]))
            alphas_f = np.linspace(0.12, 0.35, len(sel))
            future_scatter.set_color([(0.6,0.8,1.0,a) for a in alphas_f])
        else:
            future_scatter.set_offsets([])

        # small halo glow under cube when below 12 km
        halo = None
        if alt[i] < 12000:
            glow_strength = np.clip((12000.0 - alt[i]) / 12000.0, 0.0, 1.0)
            # draw a translucent circle via scatter
            halo = ax_left.scatter([rod_pixel_x], [y - cube_size_frac*0.04], s=600*glow_strength,
                                   color=(1.0,0.95,0.6,0.06+0.18*glow_strength), zorder=6)

        # event banners top-left when in window
        # clear any previous small texts (we rely on fig.texts clear below)
        for name,(sidx,eidx) in event_windows.items():
            pass  # we'll show via fig.texts clearing below

        fig.texts.clear()
        for name, (sidx, eidx) in event_windows.items():
            if sidx <= i <= eidx:
                center = (sidx + eidx) / 2.0
                dist = abs(i - center) / max(1.0, (eidx - sidx) / 2.0)
                alpha = np.clip(1.0 - dist, 0.25, 1.0)
                fig.text(0.03, 0.94, name, fontsize=20, color=(1,0.95,0.85,alpha),
                         bbox=dict(boxstyle="round,pad=0.4", facecolor=(0,0,0,0.6*alpha)))

        # HUD line bottom-right with timestamp (small)
        ts = df["timestamp"].iloc[i].strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.70, 0.03, f"t={ts} | Alt={alt[i]:.0f} m", fontsize=10, color="white")

        # grab frame
        writer.grab_frame(facecolor=fig.get_facecolor())

print("Export complete ->", OUT_FILE)
