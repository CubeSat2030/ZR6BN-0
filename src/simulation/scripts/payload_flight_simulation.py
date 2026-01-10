#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import matplotlib
# Force headless to save RAM
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
import matplotlib.gridspec as gridspec

# --- LEAN CONFIG ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "2_inflight", "MPU6050.txt")
SUBSAMPLE_RATE = 5
RENDER_DPI = 50
CUBE_SIZE = 0.12

# --- DATA LOADING ---
cols = ["timestamp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
df = pd.read_csv(DATA_FILE, comment="#", usecols=cols, low_memory=False)
df = df.iloc[::SUBSAMPLE_RATE].reset_index(drop=True)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

# Use float32 for 500MB RAM safety
accel = df[["accel_x", "accel_y", "accel_z"]].to_numpy(dtype=np.float32)
gyro = df[["gyro_x", "gyro_y", "gyro_z"]].to_numpy(dtype=np.float32)
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values.astype(np.float32)
dt = np.diff(times, prepend=times[0])

# --- FIXED ORIENTATION INTEGRATION ---
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro[i] * dt[i]
    # FIX: Only rotate if there is actual movement to avoid Zero Norm Quaternions
    if np.any(omega): 
        step_rotation = R.from_rotvec(omega)
        orientations.append(orientations[-1] * step_rotation)
    else:
        orientations.append(orientations[-1])

rotations = [r.as_matrix().astype(np.float32) for r in orientations]

# --- VISUALS ---
L = CUBE_SIZE / 2.0
verts = np.array([[-L,-L,-L], [L,-L,-L], [L,L,-L], [-L,L,-L],
                  [-L,-L,L], [L,-L,L], [L,L,L], [-L,L,L]], dtype=np.float32)
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]

plt.style.use("dark_background")
fig = plt.figure(figsize=(10, 6))
gs = gridspec.GridSpec(1, 2, width_ratios=[1.5, 1.0])

ax3d = fig.add_subplot(gs[0], projection="3d")
ax3d.set_xlim([-0.2, 0.2]); ax3d.set_ylim([-0.2, 0.2]); ax3d.set_zlim([-0.2, 0.2])
ax3d.axis('off')

ax_telemetry = fig.add_subplot(gs[1])
ax_telemetry.plot(times, accel[:, 2], lw=0.5, color='cyan', label='Accel Z')
ax_telemetry.set_title("Telemetry (Subsampled)", fontsize=8)
time_marker = ax_telemetry.axvline(times[0], color="gold", lw=1)

poly = Poly3DCollection([], facecolors='orange', edgecolors='white', lw=0.5)
ax3d.add_collection3d(poly)

# --- UPDATE LOOP ---
def update(frame):
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])
    time_marker.set_xdata([times[frame], times[frame]])
    ax3d.view_init(elev=20, azim=frame * 1.5)
    return [poly, time_marker]

# --- RENDER ---
ani = FuncAnimation(fig, update, frames=len(df), blit=True)

try:
    print("Starting render on 500MB RAM system...")
    ani.save("BACAR13_fixed_replay.mp4", fps=20, dpi=RENDER_DPI, writer='ffmpeg', bitrate=800)
    print("Success: BACAR13_fixed_replay.mp4")
except Exception as e:
    print(f"Render failed: {e}")
