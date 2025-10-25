#!/usr/bin/env python3
"""
simulate_payload_flight.py — Kinematic Replay (Option A)

Usage:
    python simulate_payload_flight.py --input /path/to/MPU6050_enhanced_physics.txt \
        [--output flight_animation.mp4] [--nominal-rate 10]

What it does:
 - Loads the enhanced physics txt (skips header comment lines starting with '#').
 - Interprets `velocity_m_s` as vertical speed (m/s). If missing, integrates `linear_accel_z_m_s2`.
 - Integrates vertical velocity to reconstruct altitude (initial altitude = 0 m).
 - Integrates gyro rates to reconstruct yaw/pitch/roll (simple integration).
 - Writes a reconstructed txt with an added `recon_altitude_m` column next to original fields.
 - Optionally renders an MP4 animation (requires ffmpeg installed).
Notes:
 - Sampling uses real timestamps if present; otherwise uses nominal-rate (default 10 Hz).
 - Orientation integration is basic dead-reckoning (no sensor fusion).
"""
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
from io import StringIO
import os

def load_enhanced_txt(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    # Keep only non-comment lines
    data_lines = [ln for ln in lines if not ln.lstrip().startswith('#') and ln.strip()!='']
    if len(data_lines) == 0:
        raise RuntimeError("No data lines found in file (all header or empty).")
    text = ''.join(data_lines)
    df = pd.read_csv(StringIO(text), header=0)
    # try parsing timestamp
    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        except Exception:
            pass
    return df

def compute_time_array(df, nominal_rate_hz):
    if 'timestamp' in df.columns and df['timestamp'].notna().sum() > 1:
        t = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds().to_numpy()
    else:
        dt = 1.0 / float(nominal_rate_hz)
        t = np.arange(len(df)) * dt
    return t

def compute_vertical_velocity(df, t):
    # Prefer velocity_m_s if present
    if 'velocity_m_s' in df.columns and df['velocity_m_s'].notna().sum() > 0:
        vz = df['velocity_m_s'].fillna(method='ffill').fillna(0.0).to_numpy()
    elif 'linear_accel_z_m_s2' in df.columns:
        a = df['linear_accel_z_m_s2'].fillna(0.0).to_numpy()
        vz = np.zeros_like(a)
        for i in range(1,len(a)):
            dt = t[i] - t[i-1]
            vz[i] = vz[i-1] + 0.5*(a[i] + a[i-1]) * dt
    else:
        vz = np.zeros(len(df))
    return vz

def integrate_altitude(vz, t):
    z = np.zeros_like(vz)
    for i in range(1,len(vz)):
        dt = t[i] - t[i-1]
        z[i] = z[i-1] + 0.5 * (vz[i] + vz[i-1]) * dt
    return z

def integrate_gyro(df, t):
    n = len(df)
    gx = df['gyro_x_rads'].fillna(0.0).to_numpy() if 'gyro_x_rads' in df.columns else np.zeros(n)
    gy = df['gyro_y_rads'].fillna(0.0).to_numpy() if 'gyro_y_rads' in df.columns else np.zeros(n)
    gz = df['gyro_z_rads'].fillna(0.0).to_numpy() if 'gyro_z_rads' in df.columns else np.zeros(n)
    roll = np.zeros(n); pitch = np.zeros(n); yaw = np.zeros(n)
    for i in range(1,n):
        dt = t[i] - t[i-1]
        roll[i] = roll[i-1] + gx[i] * dt
        pitch[i] = pitch[i-1] + gy[i] * dt
        yaw[i] = yaw[i-1] + gz[i] * dt
    return yaw, pitch, roll

def save_reconstructed(df, z, input_path):
    out_df = df.copy()
    out_df['recon_altitude_m'] = z
    base = os.path.splitext(input_path)[0]
    out_path = base + '_recon.txt'
    out_df.to_csv(out_path, index=False)
    return out_path

def animate_simple(z, t, df, out_file=None, fps=10):
    # 3D rod animation (simple): x,y from small roll/pitch deflections, z from recon altitude
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure(figsize=(6,8))
    ax = fig.add_subplot(111, projection='3d')
    # set broad axis limits for presentation
    zmin = float(np.nanmin(z)); zmax = float(np.nanmax(z))
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_zlim(zmin - 50, zmax + 50)
    rod_line, = ax.plot([], [], [], lw=3, marker='o')

    # try to get roll/pitch for small visual tilts if present
    yaw, pitch, roll = (np.zeros_like(z), np.zeros_like(z), np.zeros_like(z))
    if 'gyro_x_rads' in df.columns:
        yaw, pitch, roll = integrate_gyro(df, t)  # note: integrate_gyro signature different; we'll reuse below instead
    # fallback small arrays
    def init():
        rod_line.set_data([], [])
        rod_line.set_3d_properties([])
        return (rod_line,)

    def update(i):
        zi = z[i]
        L = 10.0
        rx = np.sin(0.0) * L
        ry = np.sin(0.0) * L
        x = (-rx, rx)
        y = (-ry, ry)
        zs = (zi - 0.5*L, zi + 0.5*L)
        rod_line.set_data(x, y)
        rod_line.set_3d_properties(zs)
        ax.set_title(f"t={t[i]:.1f}s  z={zi:.1f} m")
        return (rod_line,)

    anim = animation.FuncAnimation(fig, update, frames=len(z), init_func=init, blit=False, interval=1000.0/fps)
    if out_file:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=fps, metadata=dict(artist='sim'), bitrate=2000)
        anim.save(out_file, writer=writer)
    return anim

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', default='MPU6050_enhanced_physics.txt')
    p.add_argument('--output', '-o', default='')  # if set, will render mp4
    p.add_argument('--nominal-rate', '-r', type=float, default=10.0)
    args = p.parse_args()

    df = load_enhanced_txt(args.input)
    t = compute_time_array(df, args.nominal_rate)
    vz = compute_vertical_velocity(df, t)
    z = integrate_altitude(vz, t)
    yaw, pitch, roll = integrate_gyro(df, t)

    recon_path = save_reconstructed(df, z, args.input)
    print(f"Reconstructed file saved: {recon_path}")

    if args.output:
        print("Rendering animation (may take time). Output:", args.output)
        # Try to animate and save to file
        anim = animate_simple(z, t, df, out_file=args.output, fps=int(args.nominal_rate))
        print("Animation saved.")

if __name__ == "__main__":
    main()
