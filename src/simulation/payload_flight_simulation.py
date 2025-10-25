#!/usr/bin/env python3
"""
replay_flight_from_mpu6050.py
---------------------------------
Kinematic Replay Simulation

Recreates the payload's true trajectory and attitude from recorded MPU6050 data.
- Loads src/logger/data/MPU6050_enhanced_physics.txt
- Integrates vertical velocity (or linear_accel_z) to reconstruct altitude.
- Integrates gyro rates to compute yaw, pitch, roll (basic dead-reckoning).
- Outputs: reconstructed .txt, optional MP4 replay.
- Textbook-accurate: all calculations in SI units, no smoothing.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
from io import StringIO
from pathlib import Path

DATA_PATH = Path(__file__).parents[1] / "logger" / "data" / "MPU6050_enhanced_physics.txt"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_enhanced_txt(path):
    with open(path, "r") as f:
        lines = [ln for ln in f.readlines() if not ln.lstrip().startswith("#") and ln.strip()]
    df = pd.read_csv(StringIO("".join(lines)), header=0)
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        except Exception:
            pass
    return df

def compute_time(df, nominal_rate=10.0):
    if "timestamp" in df.columns and df["timestamp"].notna().sum() > 1:
        return (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().to_numpy()
    else:
        return np.arange(len(df)) * (1.0 / nominal_rate)

def compute_velocity(df, t):
    if "velocity_m_s" in df.columns and df["velocity_m_s"].notna().sum() > 0:
        return df["velocity_m_s"].fillna(method="ffill").fillna(0).to_numpy()
    elif "linear_accel_z_m_s2" in df.columns:
        a = df["linear_accel_z_m_s2"].fillna(0).to_numpy()
        v = np.zeros_like(a)
        for i in range(1, len(a)):
            dt = t[i] - t[i-1]
            v[i] = v[i-1] + 0.5 * (a[i] + a[i-1]) * dt
        return v
    else:
        return np.zeros(len(df))

def integrate_altitude(v, t):
    z = np.zeros_like(v)
    for i in range(1, len(v)):
        dt = t[i] - t[i-1]
        z[i] = z[i-1] + 0.5 * (v[i] + v[i-1]) * dt
    return z

def integrate_gyro(df, t):
    n = len(df)
    gx = df.get("gyro_x_rads", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    gy = df.get("gyro_y_rads", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    gz = df.get("gyro_z_rads", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    roll = np.zeros(n); pitch = np.zeros(n); yaw = np.zeros(n)
    for i in range(1, n):
        dt = t[i] - t[i-1]
        roll[i] = roll[i-1] + gx[i] * dt
        pitch[i] = pitch[i-1] + gy[i] * dt
        yaw[i] = yaw[i-1] + gz[i] * dt
    return yaw, pitch, roll

def save_reconstruction(df, z):
    out_df = df.copy()
    out_df["recon_altitude_m"] = z
    out_path = OUTPUT_DIR / "MPU6050_reconstructed.txt"
    out_df.to_csv(out_path, index=False)
    print(f"[✓] Saved reconstructed file: {out_path}")
    return out_path

def plot_altitude(t, z):
    plt.figure(figsize=(10,4))
    plt.plot(t, z, linewidth=0.9)
    plt.xlabel("Time (s)")
    plt.ylabel("Altitude (m)")
    plt.title("Reconstructed Altitude — Kinematic Replay")
    plt.grid(True)
    out_img = OUTPUT_DIR / "altitude_profile.png"
    plt.tight_layout()
    plt.savefig(out_img)
    plt.close()
    print(f"[✓] Altitude plot saved: {out_img}")

def replay_animation(t, z, out_file):
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure(figsize=(6,8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim(-50,50); ax.set_ylim(-50,50)
    ax.set_zlim(min(z)-50, max(z)+50)
    ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)"); ax.set_zlabel("Altitude (m)")
    rod, = ax.plot([], [], [], lw=3, color="blue")

    def init(): rod.set_data([], []); rod.set_3d_properties([]); return (rod,)
    def update(i):
        zi = z[i]; L = 10.0
        rod.set_data([-L/2, L/2], [0, 0])
        rod.set_3d_properties([zi - L/2, zi + L/2])
        ax.set_title(f"t={t[i]:.1f}s, Alt={zi:.1f} m")
        return (rod,)

    anim = animation.FuncAnimation(fig, update, frames=len(z), init_func=init, blit=False, interval=100)
    anim.save(out_file, writer=animation.FFMpegWriter(fps=10))
    print(f"[✓] Replay video saved: {out_file}")

def main():
    print("[...] Loading data...")
    df = load_enhanced_txt(DATA_PATH)
    t = compute_time(df, nominal_rate=10.0)
    v = compute_velocity(df, t)
    z = integrate_altitude(v, t)
    yaw, pitch, roll = integrate_gyro(df, t)
    recon_file = save_reconstruction(df, z)
    plot_altitude(t, z)
    # Optional animation
    out_video = OUTPUT_DIR / "MPU6050_replay.mp4"
    print("[...] Rendering 3D replay video (this can take a few minutes)...")
    replay_animation(t, z, out_video)
    print("[✓] Simulation complete.")

if __name__ == "__main__":
    main()
