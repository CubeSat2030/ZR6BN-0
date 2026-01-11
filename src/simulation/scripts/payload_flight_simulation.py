#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Manditory for 500MB RAM
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.gridspec as gridspec

# --- LEAN CONFIG ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "", ""))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "2_inflight", "MPU6050.txt")
SUBSAMPLE_RATE = 5 
RENDER_DPI = 50
CUBE_SIZE = 0.12

# --- DATA LOADING (Minimal Memory Footprint) ---
cols = ["timestamp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
try:
    # usecols prevents loading unnecessary data into RAM
    df = pd.read_csv(DATA_FILE, comment="#", usecols=cols, low_memory=False)
    df = df.iloc[::SUBSAMPLE_RATE].reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).reset_index(drop=True)
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

# Using float32 to keep data size small
accel = df[["accel_x", "accel_y", "accel_z"]].to_numpy(dtype=np.float32)
gyro = df[["gyro_x", "gyro_y", "gyro_z"]].to_numpy(dtype=np.float32)
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values.astype(np.float32)
dt = np.diff(times, prepend=times[0])

# --- MANUAL QUATERNION MATH ---
def quat_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ], dtype=np.float32)

def quat_to_mat(q):
    w, x, y, z = q
    return np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w,     2*x*z + 2*y*w],
        [2*x*y + 2*z*w,     1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w,     2*y*z + 2*x*w,     1 - 2*x*x - 2*y*y]
    ], dtype=np.float32)

# THE LIST: Contiguous NumPy block for memory stability
q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
rotations = np.zeros((len(df), 3, 3), dtype=np.float32)

for i in range(len(df)):
    vec = gyro[i] * dt[i]
    angle = np.linalg.norm(vec)
    if angle > 1e-9:
        axis = vec / angle
        s = np.sin(angle / 2.0)
        dq = np.array([np.cos(angle / 2.0), axis[0]*s, axis[1]*s, axis[2]*s], dtype=np.float32)
        q = quat_mult(q, dq)
        q /= np.linalg.norm(q) # Prevents the Zero-Norm error
    rotations[i] = quat_to_mat(q)

# --- VISUALS ---
L = CUBE_SIZE / 2.0
verts = np.array([[-L,-L,-L], [L,-L,-L], [L,L,-L], [-L,L,-L],
                  [-L,-L,L], [L,-L,L], [L,L,L], [-L,L,L]], dtype=np.float32)
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]

plt.style.use("dark_background")
fig = plt.figure(figsize=(8, 5))
gs = gridspec.GridSpec(1, 2, width_ratios=[1.2, 1.0])

ax3d = fig.add_subplot(gs[0], projection='3d')
ax3d.set_xlim([-0.2, 0.2]); ax3d.set_ylim([-0.2, 0.2]); ax3d.set_zlim([-0.2, 0.2])
ax3d.axis('off')

ax_tele = fig.add_subplot(gs[1])
ax_tele.plot(times, accel[:, 2], lw=0.5, color='lime')
time_marker = ax_tele.axvline(times[0], color="gold", lw=1)

poly = Poly3DCollection([], facecolors='cyan', edgecolors='white', lw=0.3)
ax3d.add_collection3d(poly)

# --- UPDATE WITH PROGRESS PRINT ---
def update(frame):
    if frame % 25 == 0: # Print update every 25 frames
        sys.stdout.write(f"\r[PROCESS] Rendering frame {frame}/{len(df)}")
        sys.stdout.flush()
    
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])
    time_marker.set_xdata([times[frame], times[frame]])
    ax3d.view_init(elev=20, azim=frame * 1.5)
    return [poly, time_marker]

# --- RENDER ---
ani = FuncAnimation(fig, update, frames=len(df), blit=True)

print(f"Starting memory-locked render...")
try:
    # Low bitrate and FPS to prevent FFmpeg from crashing the 500MB RAM pipe
    ani.save("BACAR13_stable_replay.mp4", fps=15, dpi=RENDER_DPI, writer='ffmpeg', bitrate=400)
    sys.stdout.write(f"\r[SUCCESS] Final frame {len(df)}/{len(df)} reached. Export saved.\n")
except Exception as e:
    print(f"\n[CRITICAL] Render failed: {e}")
