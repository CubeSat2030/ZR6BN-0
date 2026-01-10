#!/usr/bin/env python3
"""
BACAR-13 Cinematic Payload Flight Simulation
Optimized for 10GB RAM systems.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial.transform import Rotation as R
import matplotlib.gridspec as gridspec

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "2_inflight", "MPU6050.txt")

REALTIME_SPEED = 1.0
CUBE_SIZE = 0.12
ACC_SCALE = 0.015
TRAIL_LENGTH = 50  # Reduced slightly for memory
RENDER_DPI = 100   # Critical fix for 10GB RAM (reduces frame buffer size)
SUBSAMPLE_RATE = 1 # Set to 2 or 3 if you still hit RAM limits to skip rows

MAX_ALTITUDE_CLIP = 32000.0

# ------------------------------------------------------------------
# LOAD & PREP DATA
# ------------------------------------------------------------------
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"MPU6050 file not found at: {DATA_FILE}")

# Use low_memory=False to suppress DtypeWarning
df = pd.read_csv(DATA_FILE, comment="#", low_memory=False)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

# Subsampling to stay within 10GB RAM if necessary
if SUBSAMPLE_RATE > 1:
    df = df.iloc[::SUBSAMPLE_RATE].reset_index(drop=True)

COLUMN_MAP = {
    "accel_x": "accel_x_m_s2", "accel_y": "accel_y_m_s2", "accel_z": "accel_z_m_s2",
    "gyro_x": "gyro_x_rads", "gyro_y": "gyro_y_rads", "gyro_z": "gyro_z_rads",
}
df = df.rename(columns=COLUMN_MAP)

# Clean numeric columns properly
df = df.infer_objects(copy=False)
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].interpolate().fillna(0)
df = df.sort_values(by="timestamp").reset_index(drop=True)

if "velocity_m_s" not in df.columns:
    df["velocity_m_s"] = 0.0

times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
gyro = df[["gyro_x_rads", "gyro_y_rads", "gyro_z_rads"]].to_numpy()
accel = df[["accel_x_m_s2", "accel_y_m_s2", "accel_z_m_s2"]].to_numpy()
vel = df["velocity_m_s"].to_numpy()

# Integrate altitude
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i] * dt[i]
alt = np.clip(alt, 0, MAX_ALTITUDE_CLIP)

# Integrate orientation
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro[i] * dt[i]
    orientations.append(orientations[-1] * R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

# ------------------------------------------------------------------
# GEOMETRY & STYLING
# ------------------------------------------------------------------
L = CUBE_SIZE / 2.0
verts = np.array([[-L,-L,-L], [L,-L,-L], [L,L,-L], [-L,L,-L],
                  [-L,-L,L], [L,-L,L], [L,L,L], [-L,L,L]])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]

plt.style.use("dark_background")
fig = plt.figure(figsize=(18, 10))
gs = gridspec.GridSpec(1, 2, width_ratios=[2.0, 1.0], wspace=0.12)

ax3d = fig.add_subplot(gs[0], projection="3d")
ax3d.set_box_aspect((1,1,1))
ax3d.set_xlim([-L*5, L*5]); ax3d.set_ylim([-L*5, L*5]); ax3d.set_zlim([-L*5, L*5])
ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])

right_gs = gs[1].subgridspec(6, 1, hspace=0.35)
ax_accel = fig.add_subplot(right_gs[0])
ax_gyro  = fig.add_subplot(right_gs[1], sharex=ax_accel)
ax_vel   = fig.add_subplot(right_gs[2], sharex=ax_accel)
ax_alt_t = fig.add_subplot(right_gs[3], sharex=ax_accel)
ax_mag   = fig.add_subplot(right_gs[4], sharex=ax_accel)
ax_dummy = fig.add_subplot(right_gs[5], sharex=ax_accel)

# Static Plotting
ax_accel.plot(df["timestamp"], df["accel_x_m_s2"], label="ax", lw=0.7)
ax_accel.plot(df["timestamp"], df["accel_y_m_s2"], label="ay", lw=0.7)
ax_accel.plot(df["timestamp"], df["accel_z_m_s2"], label="az", lw=0.7)
ax_gyro.plot(df["timestamp"], df["gyro_x_rads"], label="gx", lw=0.7)
ax_gyro.plot(df["timestamp"], df["gyro_y_rads"], label="gy", lw=0.7)
ax_gyro.plot(df["timestamp"], df["gyro_z_rads"], label="gz", lw=0.7)
ax_vel.plot(df["timestamp"], df["velocity_m_s"], label="vel", lw=0.8)
ax_alt_t.plot(df["timestamp"], alt, label="alt", lw=0.8, color="#42A5F5")
mag = np.linalg.norm(accel, axis=1)
ax_mag.plot(df["timestamp"], mag, label="|a|", lw=0.8, color="#FFD54F")

time_markers = [a.axvline(df["timestamp"].iloc[0], color="gold", lw=1.5) for a in [ax_accel, ax_gyro, ax_vel, ax_alt_t, ax_mag]]

# 3D Artists
poly = Poly3DCollection([], facecolors=(1.0, 0.84, 0.4), edgecolors="#2a2a2a", lw=0.6)
ax3d.add_collection3d(poly)
past_line, = ax3d.plot([], [], [], lw=2, alpha=0.6)
# Use a single point for the vector to avoid re-creating quiver objects (RAM hog)
acc_vector, = ax3d.plot([], [], [], color="cyan", lw=2)

# Trail
trail_collection = Line3DCollection([], colors=[(0.2, 0.8, 1.0, 0.2)], lw=2)
ax3d.add_collection3d(trail_collection)

def altitude_to_color(h):
    t = np.clip(h / 32000.0, 0, 1)
    if h > 12000:
        return (0.15*(1-t), 0.05+0.45*(1-t), 0.1+0.9*(1-t/2))
    return (0.1+0.4*(h/12000), 0.3+0.4*(h/12000), 0.5+0.5*(h/12000))

# ------------------------------------------------------------------
# UPDATE FUNCTION
# ------------------------------------------------------------------
trail_pts = []

def update(frame):
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])

    # Accel vector update (Fixed line instead of Quiver for RAM)
    acc_world = Rm @ (accel[frame] * ACC_SCALE)
    acc_vector.set_data([0, acc_world[0]], [0, acc_world[1]])
    acc_vector.set_3d_properties([0, acc_world[2]])

    # Trail Management
    global trail_pts
    trail_pts.append(acc_world)
    if len(trail_pts) > TRAIL_LENGTH: trail_pts.pop(0)
    if len(trail_pts) > 1:
        segs = [[trail_pts[i], trail_pts[i+1]] for i in range(len(trail_pts)-1)]
        trail_collection.set_segments(segs)

    # UI/Background
    bg = altitude_to_color(alt[frame])
    fig.patch.set_facecolor(bg)
    ax3d.set_facecolor(bg)
    
    current_ts = df["timestamp"].iloc[frame]
    for ln in time_markers:
        ln.set_xdata([current_ts, current_ts])

    ax3d.view_init(elev=20, azim=frame * 0.5)
    fig.suptitle(f"BACAR-13 | Alt: {alt[frame]:.0f}m | Time: {times[frame]:.1f}s", color="white")
    
    return [poly, acc_vector, trail_collection] + time_markers

# ------------------------------------------------------------------
# EXECUTION
# ------------------------------------------------------------------
ani = FuncAnimation(fig, update, frames=len(df), blit=False)

# Optimization: Save FIRST, then Show. 
# 3600x2000 was the old size. DPI 100 makes it 1800x1000 (much safer).
print(f"Rendering video at {RENDER_DPI} DPI... this may take a few minutes.")
try:
    ani.save("BACAR13_cinematic_replay.mp4", fps=30, dpi=RENDER_DPI, writer='ffmpeg')
    print("Video saved successfully.")
except Exception as e:
    print(f"Error saving video: {e}")

# If you want to see the plot after saving
# plt.show()
