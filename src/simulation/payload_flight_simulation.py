#!/usr/bin/env python3
"""
Bacar-13 Cinematic Flight Exporter (Full HD MP4, real-time fidelity)
- Uses logger/data/MPU6050.txt (confirmed path)
- Exports a Full HD MP4 (libx264) of the full flight (no time-compression) by default
- MODE = "FULL" (real-time 1:1) or "PREVIEW" (fast visual check)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial.transform import Rotation as R
from scipy.signal import savgol_filter
import matplotlib.gridspec as gridspec
import warnings

# ---------------- CONFIG ----------------
# File locations (you confirmed this path)
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "logger", "data", "MPU6050.txt")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
OUT_FILE = os.path.join(OUT_DIR, "BACAR13_full_simulation.mp4")

# Export / visual parameters
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
DPI = 150  # controls quality; higher = bigger file
CODEC = "libx264"  # you requested default
MODE = "FULL"  # "FULL" = 1:1 real-time, "PREVIEW" = accelerated short render
PREVIEW_SECONDS = 30  # if MODE == "PREVIEW", output length in seconds
PREVIEW_FPS = 24
CUBE_SIZE = 0.12
ACC_SCALE = 0.015
TRAIL_LENGTH = 80
SMOOTH_WINDOW = 51
SMOOTH_POLYORDER = 3

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------- LOAD DATA ----------------
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"MPU6050 file not found at: {DATA_FILE}")

# Read csv and allow comment lines
df = pd.read_csv(DATA_FILE, comment="#")
if "timestamp" not in df.columns:
    raise ValueError("MPU6050.txt must contain a 'timestamp' column")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

# Ensure required numeric columns exist (fallback to zeros)
required = [
    "velocity_m_s", "accel_x_m_s2", "accel_y_m_s2", "accel_z_m_s2",
    "gyro_x_dps", "gyro_y_dps", "gyro_z_dps"
]
for c in required:
    if c not in df.columns:
        df[c] = 0.0

# Sort, interpolate numeric columns
df = df.sort_values("timestamp").reset_index(drop=True)
numcols = df.select_dtypes(include=[np.number]).columns
df[numcols] = df[numcols].interpolate().fillna(0.0)

# time arrays: seconds since start
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
# fix non-positive dt entries
if np.any(dt <= 0):
    pos = dt[dt > 0]
    dt[dt <= 0] = np.mean(pos) if len(pos) else 1.0

# integrate altitude from velocity (if velocity present)
vel = df["velocity_m_s"].to_numpy(dtype=float)
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i] * dt[i]
alt = np.clip(alt, 0.0, 32000.0)

# ---------------- GYRO -> ORIENTATION ----------------
gyro_dps = df[["gyro_x_dps","gyro_y_dps","gyro_z_dps"]].to_numpy(dtype=float)
n = len(gyro_dps)
# safe smoothing
if n >= 7:
    win = SMOOTH_WINDOW if SMOOTH_WINDOW < n else (n // 2) * 2 + 1
    if win % 2 == 0:
        win -= 1
    if win < 3:
        win = 3
    try:
        gyro_smoothed = np.zeros_like(gyro_dps)
        for i in range(3):
            gyro_smoothed[:, i] = savgol_filter(gyro_dps[:, i], win, SMOOTH_POLYORDER)
    except Exception:
        gyro_smoothed = gyro_dps.copy()
else:
    gyro_smoothed = gyro_dps.copy()

# convert dps -> rad/s
gyro_rad = np.deg2rad(gyro_smoothed)

# integrate to orientations
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro_rad[i] * dt[i]  # small rotation vector (rad)
    orientations.append(orientations[-1] * R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

# ---------------- EVENT DETECTION ----------------
acc_vec = df[["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].to_numpy(dtype=float)
acc_mag = np.linalg.norm(acc_vec, axis=1)

# simple robust detection: burst = global peak; impact = last strong peak near end
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

# ---------------- ADAPTIVE FPS & FRAME MAPPING ----------------
# Compute average sampling frequency from telemetry timestamps (samples per second)
median_dt = np.median(dt[np.where(dt > 0)])
if median_dt <= 0:
    median_dt = 1.0
telemetry_rate = 1.0 / median_dt  # samples per second

# Decide FPS: preserve real-time fidelity
# Use FPS = max(1, round(telemetry_rate)).
# Cap to reasonable upper bound to avoid insane fps (e.g., 60)
fps = int(max(1, round(telemetry_rate)))
if fps > 60:
    warnings.warn(f"Telemetry sample rate {telemetry_rate:.2f}Hz > 60Hz; capping export FPS to 60.")
    fps = 60

if MODE == "PREVIEW":
    out_fps = PREVIEW_FPS
else:
    out_fps = fps

# total frames = total flight seconds * out_fps
total_seconds = int(np.ceil(times[-1] - times[0]))
total_frames = int(np.ceil((times[-1] - times[0]) * out_fps)) + 1
if total_frames <= 0:
    total_frames = len(df)

# Map each output frame to the telemetry index (nearest sample)
if MODE == "PREVIEW":
    # Preview: compress to PREVIEW_SECONDS
    total_frames = PREVIEW_SECONDS * out_fps
    selected_frames = np.linspace(0, len(df)-1, int(total_frames)).astype(int)
else:
    # Full: map each video frame time to nearest telemetry timestamp
    video_times = np.linspace(times[0], times[-1], total_frames)
    # for each video_time, find nearest telemetry sample index
    selected_frames = np.searchsorted(times, video_times, side="left")
    selected_frames[selected_frames >= len(df)] = len(df)-1

# ---------------- FIGURE & AXES ----------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(FRAME_WIDTH / DPI * 1.0, FRAME_HEIGHT / DPI * 1.0), dpi=DPI)
gs = gridspec.GridSpec(1,2, width_ratios=[2.0, 1.0], wspace=0.12)

ax3d = fig.add_subplot(gs[0], projection="3d")
ax3d.set_box_aspect((1,1,1))
ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])
ax3d.set_xlim([-0.8, 0.8]); ax3d.set_ylim([-0.8, 0.8]); ax3d.set_zlim([-0.8, 0.8])

right_gs = gs[1].subgridspec(6,1, hspace=0.35)
ax_accel = fig.add_subplot(right_gs[0])
ax_gyro  = fig.add_subplot(right_gs[1], sharex=ax_accel)
ax_vel   = fig.add_subplot(right_gs[2], sharex=ax_accel)
ax_alt_t = fig.add_subplot(right_gs[3], sharex=ax_accel)
ax_mag   = fig.add_subplot(right_gs[4], sharex=ax_accel)
ax_dummy = fig.add_subplot(right_gs[5], sharex=ax_accel)

for a in (ax_gyro, ax_vel, ax_alt_t, ax_mag, ax_dummy):
    plt.setp(a.get_xticklabels(), visible=False)
    a.grid(True, alpha=0.2)

ax_accel.set_title("BACAR-13 — MPU6050 Telemetry")
ax_accel.plot(df["timestamp"], df["accel_x_m_s2"], lw=0.6, label="ax")
ax_accel.plot(df["timestamp"], df["accel_y_m_s2"], lw=0.6, label="ay")
ax_accel.plot(df["timestamp"], df["accel_z_m_s2"], lw=0.6, label="az")
ax_accel.legend(loc="upper right", fontsize="small")

ax_gyro.plot(df["timestamp"], df["gyro_x_dps"], lw=0.6, label="gx")
ax_gyro.plot(df["timestamp"], df["gyro_y_dps"], lw=0.6, label="gy")
ax_gyro.plot(df["timestamp"], df["gyro_z_dps"], lw=0.6, label="gz")
ax_gyro.legend(loc="upper right", fontsize="small")

ax_vel.plot(df["timestamp"], df["velocity_m_s"], lw=0.8)
ax_alt_t.plot(df["timestamp"], alt, lw=0.8, color="#42A5F5")
ax_mag.plot(df["timestamp"], acc_mag, lw=0.8, color="#FFD54F")
ax_dummy.axis("off")

time_markers = []
for a in (ax_accel, ax_gyro, ax_vel, ax_alt_t, ax_mag):
    ln = a.axvline(df["timestamp"].iloc[0], color="gold", lw=1.0, alpha=0.9)
    time_markers.append(ln)

# 3D artists
L = CUBE_SIZE / 2.0
verts = np.array([
    [-L,-L,-L],[ L,-L,-L],[ L, L,-L],[-L, L,-L],
    [-L,-L, L],[ L,-L, L],[ L, L, L],[-L, L, L]
])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]

poly = Poly3DCollection([], facecolors=(1.0,0.84,0.4), edgecolors="#2a2a2a", lw=0.6, alpha=0.98)
ax3d.add_collection3d(poly)

traj_x = np.zeros_like(alt)
traj_y = np.zeros_like(alt)
traj_z = alt / (32000.0 / 3.0)  # visual scaling
past_line, = ax3d.plot([], [], [], lw=2.2, alpha=0.6)
future_line, = ax3d.plot([], [], [], lw=1.2, ls='--', alpha=0.35)

trail_buffer = np.zeros((TRAIL_LENGTH, 3))
trail_collection = Line3DCollection([[[0,0,0],[0,0,0]]], colors=[(0.2,0.6,1.0,0.12)], lw=2)
ax3d.add_collection3d(trail_collection)

theta = np.linspace(-np.pi/1.6, np.pi/1.6, 240)
horizon_radius = 2.5
x_arc = horizon_radius * np.cos(theta)
y_arc = horizon_radius * np.sin(theta)
z_arc = np.zeros_like(x_arc)
horizon_line = ax3d.plot(x_arc, y_arc, z_arc, color=(0.3,0.6,1,0.0), lw=6)[0]

halo_artist = None
impact_frame = -1

def get_poly_basecolor(default=(1.0,0.84,0.4)):
    fc = poly.get_facecolor()
    if len(fc) == 0:
        return np.array(default)
    try:
        return np.array(fc[0][:3])
    except Exception:
        return np.array(default)

def draw_event_banner(name, alpha):
    bbox = dict(boxstyle="round,pad=0.6", facecolor=(0,0,0,0.6*alpha), edgecolor=(1,1,1,0.08))
    fig.text(0.04, 0.92, name, fontsize=22, color=(1,0.95,0.8,alpha), bbox=bbox)

# ---------------- HELPER: altitude -> color gradient ----------------
def altitude_to_color(altitude):
    """
    Converts altitude (m) to a cinematic sky gradient RGB tuple.
    Sea level = warm horizon, high altitude = dark near-space blue.
    """
    # clamp altitude to 0–30 000 m range
    a = np.clip(altitude / 30000.0, 0.0, 1.0)
    # interpolate between (R,G,B)
    # ground = sunset orange, mid = sky blue, stratosphere = deep navy
    ground = np.array([0.98, 0.58, 0.20])   # orange-gold
    midsky = np.array([0.30, 0.55, 0.90])   # light blue
    highsky = np.array([0.03, 0.06, 0.12])  # near-space navy
    if a < 0.4:
        t = a / 0.4
        color = (1 - t) * ground + t * midsky
    else:
        t = (a - 0.4) / 0.6
        color = (1 - t) * midsky + t * highsky
    return tuple(np.clip(color, 0, 1))

# ---------------- EXPORT (no interactive display) ----------------
total_output_frames = len(selected_frames)
writer = FFMpegWriter(fps=out_fps, metadata=dict(artist="BACAR-13 Replay"), codec=CODEC)

print(f"Export settings: MODE={MODE} | telemetry_rate={telemetry_rate:.3f}Hz | export_fps={out_fps} | frames={total_output_frames}")
print(f"Output file: {OUT_FILE}")
print("Starting render... (this will create the MP4 file on disk)")

# The animation loop: draw frame-by-frame and write via writer.saving
with writer.saving(fig, OUT_FILE, dpi=DPI):
    for out_i in range(total_output_frames):
        frame = int(selected_frames[out_i])

        # orientation
        Rm = rotations[frame]
        rotated = (Rm @ verts.T).T
        poly.set_verts([[rotated[i] for i in f] for f in faces])

        # acceleration vector & trail
        acc_body = acc_vec[frame]
        acc_world = Rm @ (acc_body * ACC_SCALE)
        trail_buffer[:-1] = trail_buffer[1:]
        trail_buffer[-1] = acc_world
        segments = [[trail_buffer[i], trail_buffer[i+1]] for i in range(TRAIL_LENGTH-1)]
        trail_collection.set_segments(segments)

        # trajectory
        past_mask = np.arange(len(times)) <= frame
        future_mask = np.arange(len(times)) > frame
        past_line.set_data(traj_x[past_mask], traj_y[past_mask])
        past_line.set_3d_properties(traj_z[past_mask])
        future_line.set_data(traj_x[future_mask], traj_y[future_mask])
        future_line.set_3d_properties(traj_z[future_mask])

        # background and horizon
        bg = altitude_to_color(alt[frame])
        fig.patch.set_facecolor(bg)
        ax3d.set_facecolor(bg)
        horizon_strength = np.clip((5000.0 - alt[frame]) / 5000.0, 0.0, 1.0)
        horizon_line.set_color((0.3 + 0.3*horizon_strength, 0.6 + 0.2*horizon_strength, 1.0, 0.15 + 0.5*horizon_strength))
        horizon_line.set_linewidth(3.5 + 2.5*horizon_strength)

        # lighting & bloom
        if alt[frame] < 10000:
            ambient_factor = (10000.0 - alt[frame]) / 10000.0
            base = np.array([1.0, 0.84, 0.4])
            tint = np.array([0.0, 0.03, 0.12]) * ambient_factor
            poly.set_facecolor(tuple(np.clip(base + tint, 0, 1)))
        else:
            poly.set_facecolor((1.0,0.84,0.4))

        if alt[frame] < 1000:
            bloom_strength = (1000.0 - alt[frame]) / 1000.0
            base_color = get_poly_basecolor()
            poly.set_facecolor(tuple(np.clip(base_color + bloom_strength * 0.1, 0, 1)))

        # camera stabilization
        smooth_factor = np.clip((500.0 - alt[frame]) / 500.0, 0.0, 1.0)
        elev = 18 + np.sin(frame * 0.02) * (4 * (1 - smooth_factor))
        azim = frame * 0.45 * (1 - 0.02 * smooth_factor) + np.sin(frame * 0.03) * (8 * (1 - smooth_factor))
        ax3d.view_init(elev=elev, azim=azim)

        # halo
        if halo_artist is not None:
            try:
                halo_artist.remove()
            except Exception:
                pass
        halo_artist = None
        if alt[frame] < 12000:
            glow_strength = np.clip((12000.0 - alt[frame]) / 12000.0, 0.0, 1.0)
            halo_size = 1800.0 * (0.08 + 0.92 * glow_strength)
            halo_alpha = 0.02 + 0.35 * glow_strength
            halo_artist = ax3d.scatter([0], [0], [0], s=halo_size, c=[(1.0,0.84,0.4,halo_alpha)], edgecolors='none')

        # impact flash
        if impact_frame == -1 and alt[frame] <= 5.0:
            impact_frame = out_i
        if impact_frame != -1:
            elapsed = (out_i - impact_frame) / out_fps
            if elapsed < 2.0:
                flash_strength = max(0.0, 1.0 - elapsed / 2.0)
                flash_color = (1.0,1.0,1.0)
                blended = tuple(flash_color[i] * flash_strength + bg[i] * (1.0 - flash_strength) for i in range(3))
                fig.patch.set_facecolor(blended)
                ax3d.set_facecolor(blended)

        # telemetry markers
        current_ts = df["timestamp"].iloc[frame]
        for ln in time_markers:
            ln.set_xdata([current_ts,current_ts])

        # event banners (fade)
        fig.texts.clear()
        for name, (sidx,eidx) in event_windows.items():
            if sidx <= frame <= eidx:
                center = (sidx + eidx) / 2.0
                dist = abs(frame - center) / max(1.0, (eidx - sidx)/2.0)
                alpha = np.clip(1.0 - dist, 0.25, 1.0)
                draw_event_banner(name, alpha)

        # HUD
        fig.suptitle(
            f"BACAR-13 | t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | Vel={vel[frame]:.1f} m/s | |a|={acc_mag[frame]:.1f} m/s²",
            fontsize=14, color="white", y=0.96
        )

        # write current frame
        writer.grab_frame(facecolor=fig.get_facecolor())

print(f"Finished export: {OUT_FILE}")
