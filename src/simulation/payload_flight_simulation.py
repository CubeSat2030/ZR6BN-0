#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACAR-13 Cinematic Payload Flight Simulation
Author: Nathan Busse
Mission: Kabot I (BACAR-13)
"""

import os
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
from scipy.spatial.transform import Rotation as R
from tqdm import tqdm

# =========================================================================
# CONFIGURATION
# =========================================================================
DATA_FILE = "src/logger/data/MPU6050.txt"
OUT_DIR = "src/simulation/output"
os.makedirs(OUT_DIR, exist_ok=True)

OUT_FILE = os.path.join(OUT_DIR, "BACAR13_simulation.mp4")
FRAME_SIZE = (1920, 1080)
FPS = 30  # display playback speed (not telemetry rate)
REALTIME = False  # False = export MP4, True = live preview
DPI = 120

# =========================================================================
# LOAD TELEMETRY
# =========================================================================
print("📡 Loading MPU6050 flight data...")
df = pd.read_csv(DATA_FILE)

# Parse timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Derive dt and gyro radians
df["dt"] = df["timestamp"].diff().dt.total_seconds().fillna(0)
gyro_cols = ["gyro_x_dps", "gyro_y_dps", "gyro_z_dps"]
for c in gyro_cols:
    if c not in df.columns:
        df[c] = 0.0
gyro_rad = df[gyro_cols].to_numpy(np.float64) * np.pi / 180.0

# =========================================================================
# ALTITUDE ESTIMATION (SCALED)
# =========================================================================
# The burst was confirmed at ~32 km altitude
ascent_duration = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
t = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
altitude = np.clip((t / ascent_duration) * 32000, 0, 32000)
df["altitude_m"] = altitude

# =========================================================================
# ORIENTATION INTEGRATION (SAFE)
# =========================================================================
print("🧭 Integrating orientation...")

orientations = [R.identity()]
for i in range(1, len(gyro_rad)):
    omega = gyro_rad[i] * df["dt"].iloc[i]

    if not np.isfinite(omega).all():
        omega = np.zeros(3)

    norm = np.linalg.norm(omega)
    if norm < 1e-12 or norm > 1e2:
        omega = np.zeros(3)

    try:
        delta_r = R.from_rotvec(omega)
    except Exception:
        delta_r = R.identity()

    orientations.append(orientations[-1] * delta_r)
    if i % 1000 == 0:
        q = orientations[-1].as_quat()
        orientations[-1] = R.from_quat(q / np.linalg.norm(q))

rotations = np.array([r.as_matrix() for r in orientations])

# =========================================================================
# ALTITUDE TO COLOR MAP
# =========================================================================
def altitude_to_color(alt_m):
    """Map altitude (0–32 km) to a cinematic sky gradient"""
    norm = np.clip(alt_m / 32000.0, 0, 1)
    r = 0.1 + 0.4 * norm
    g = 0.2 + 0.6 * norm
    b = 0.6 + 0.4 * (1 - norm)
    return (r, g, b)

# =========================================================================
# SETUP VISUALS
# =========================================================================
fig = plt.figure(figsize=(FRAME_SIZE[0]/DPI, FRAME_SIZE[1]/DPI), dpi=DPI)
ax = fig.add_subplot(111, projection="3d")

ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
ax.set_facecolor("black")
fig.patch.set_facecolor("black")

ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
ax.set_box_aspect([1,1,1])

plt.tight_layout()

# =========================================================================
# DRAW CUBOID PAYLOAD
# =========================================================================
def draw_payload(ax, Rmat, color):
    """Draw a small cuboid payload representing the probe"""
    size = 0.1
    cube = np.array([
        [-size, -size, -size],
        [ size, -size, -size],
        [ size,  size, -size],
        [-size,  size, -size],
        [-size, -size,  size],
        [ size, -size,  size],
        [ size,  size,  size],
        [-size,  size,  size],
    ])
    cube_rot = cube @ Rmat.T
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]
    for (i,j) in edges:
        ax.plot3D(
            [cube_rot[i,0], cube_rot[j,0]],
            [cube_rot[i,1], cube_rot[j,1]],
            [cube_rot[i,2], cube_rot[j,2]],
            color=color,
            linewidth=2.0,
        )

# =========================================================================
# FRAME RENDER FUNCTION
# =========================================================================
def render_frame(i):
    ax.cla()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_facecolor("black")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])

    color = altitude_to_color(df["altitude_m"].iloc[i])
    draw_payload(ax, rotations[i], color)

    ax.set_title(
        f"BACAR-13 Payload Simulation\nTime: {df['timestamp'].iloc[i].time()} | Alt: {df['altitude_m'].iloc[i]:.0f} m",
        color="white", fontsize=14
    )
    return ax,

# =========================================================================
# SIMULATION MODE SELECTION
# =========================================================================
nframes = len(df)
print(f"🎞️ Preparing {nframes} frames at 1920×1080...")

if REALTIME:
    ani = animation.FuncAnimation(fig, render_frame, frames=nframes, interval=1000/FPS, blit=False)
    plt.show()
else:
    # Export MP4 directly
    print("🎥 Rendering directly to MP4 file...")
    metadata = {
        'title': 'BACAR-13 Flight Simulation',
        'artist': 'Nathan Busse',
        'comment': 'Cinematic telemetry playback'
    }
    writer = FFMpegWriter(fps=FPS, metadata=metadata)

    with writer.saving(fig, OUT_FILE, DPI):
        for i in tqdm(range(nframes), desc="Rendering frames"):
            render_frame(i)
            writer.grab_frame()

    plt.close(fig)
    print(f"\n✅ Simulation complete — MP4 saved to: {OUT_FILE}")
