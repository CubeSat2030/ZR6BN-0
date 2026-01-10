#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import matplotlib
# Force headless mode BEFORE importing pyplot
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
import matplotlib.gridspec as gridspec

# ------------------------------------------------------------------
# ULTRA-LEAN CONFIGURATION
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "2_inflight", "MPU6050.txt")

# CRITICAL FOR 500MB RAM:
SUBSAMPLE_RATE = 5  # Skip rows to keep the dataframe small
RENDER_DPI = 50     # Very low resolution to prevent memory spikes
TRAIL_LENGTH = 20   # Short trail to save memory
CUBE_SIZE = 0.12

# ------------------------------------------------------------------
# DATA LOADING (Optimized)
# ------------------------------------------------------------------
# Read only necessary columns to save RAM immediately
cols_to_use = ["timestamp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
df = pd.read_csv(DATA_FILE, comment="#", usecols=cols_to_use, low_memory=False)

# Subsample immediately before processing
df = df.iloc[::SUBSAMPLE_RATE].reset_index(drop=True)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

# Convert to float32 to save 50% memory over default float64
accel = df[["accel_x", "accel_y", "accel_z"]].to_numpy(dtype=np.float32)
gyro = df[["gyro_x", "gyro_y", "gyro_z"]].to_numpy(dtype=np.float32)
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values.astype(np.float32)
dt = np.diff(times, prepend=times[0])

# Pre-calculate rotations to avoid complex math in the animation loop
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro[i] * dt[i]
    orientations.append(orientations[-1] * R.from_rotvec(omega))
rotations = [r.as_matrix().astype(np.float32) for r in orientations]

# ------------------------------------------------------------------
# LEAN VISUALS
# ------------------------------------------------------------------
L = CUBE_SIZE / 2.0
verts = np.array([[-L,-L,-L], [L,-L,-L], [L,L,-L], [-L,L,-L],
                  [-L,-L,L], [L,-L,L], [L,L,L], [-L,L,L]], dtype=np.float32)
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]

plt.style.use("dark_background")
fig = plt.figure(figsize=(12, 7)) # Smaller figure size
gs = gridspec.GridSpec(1, 2, width_ratios=[1.5, 1.0])

ax3d = fig.add_subplot(gs[0], projection="3d")
ax3d.set_xlim([-0.5, 0.5]); ax3d.set_ylim([-0.5, 0.5]); ax3d.set_zlim([-0.5, 0.5])
ax3d.axis('off') # Hide axes to save render cycles

ax_telemetry = fig.add_subplot(gs[1])
ax_telemetry.plot(times, accel[:, 0], lw=0.5, alpha=0.7)
time_marker = ax_telemetry.axvline(times[0], color="gold", lw=1)

poly = Poly3DCollection([], facecolors='orange', edgecolors='white', lw=0.5)
ax3d.add_collection3d(poly)

# ------------------------------------------------------------------
# RENDER LOOP
# ------------------------------------------------------------------
def update(frame):
    # Update Payload
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])
    
    # Update UI
    time_marker.set_xdata([times[frame], times[frame]])
    ax3d.view_init(elev=20, azim=frame * 2)
    
    return [poly, time_marker]

ani = FuncAnimation(fig, update, frames=len(df), blit=True)

print(f"RAM-Constrained Render Starting...")
print(f"Processing {len(df)} frames at {RENDER_DPI} DPI.")

try:
    # We use a lower bitrate to keep the FFmpeg buffer small
    ani.save("BACAR13_lean_replay.mp4", 
             fps=20, 
             dpi=RENDER_DPI, 
             writer='ffmpeg',
             bitrate=1000)
    print("Render Complete!")
except Exception as e:
    print(f"Render failed. Likely OOM: {e}")
