#!/usr/bin/env python3
"""
simulation.py

Full HAB Payload Flight Vector Simulation from MPU6050 data

Features:

• Loads post-flight MPU6050 data (timestamp, ax, ay, az, gx, gy, gz)
• Computes orientation via Madgwick AHRS filter
• Split-screen render:
    Left  → 3D payload cube + rod
    Right → Scrolling telemetry (accel mag, gyro mag, Euler angles)
• Exports directly to MP4 (no realtime playback required)


Default paths:
    Input : src/logger/data/MPU6050.txt
    Output: output/payload_simulation.mp4

Usage:
    python simulation.py
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D, art3d  # noqa: F401
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# ========================================================
# Madgwick AHRS (minimal IMU version)
# ========================================================

class MadgwickAHRS:
    def __init__(self, sample_period=1/256.0, beta=0.1):
        self.sample_period = sample_period
        self.beta = beta
        self.q = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)

    @staticmethod
    def _normalize(v):
        n = np.linalg.norm(v)
        return v if n == 0 else v / n

    def update_imu(self, gyro, accel):
        q1, q2, q3, q4 = self.q
        ax, ay, az = self._normalize(accel)
        gx, gy, gz = gyro

        # Gradient descent step
        _2q1, _2q2, _2q3, _2q4 = 2*q1, 2*q2, 2*q3, 2*q4
        _4q1, _4q2, _4q3 = 4*q1, 4*q2, 4*q3
        q1q1, q2q2, q3q3, q4q4 = q1*q1, q2*q2, q3*q3, q4*q4

        # Gradient measured from accelerometer
        s1 = _4q1*q3q3 + _2q3*ax + _4q1*q2q2 - _2q2*ay
        s2 = _4q2*q4q4 - _2q4*ax + 4*q1q1*q2 - _2q1*ay - _4q2 + 8*q2q2*q2 + 8*q2q3*q3 + _4q2*az
        s3 = 4*q1q1*q3 + _2q1*ax + _4q3*q4q4 - _2q4*ay - _4q3 + 8*q2q2*q3 + 8*q3*q3*q3 + _4q3*az
        s4 = 4*q2q2*q4 - _2q2*ax + 4*q3q3*q4 - _2q3*ay
        s = np.array([s1, s2, s3, s4])
        s = self._normalize(s)

        # Gyroscope integration
        q_dot = 0.5 * np.array([
            -q2*gx - q3*gy - q4*gz,
             q1*gx + q3*gz - q4*gy,
             q1*gy - q2*gz + q4*gx,
             q1*gz + q2*gy - q3*gx
        ]) - self.beta * s

        self.q += q_dot * self.sample_period
        self.q = self._normalize(self.q)

    def quaternion(self):
        return self.q.copy()


# ========================================================
# Quaternion helpers
# ========================================================

def quat_to_euler(q):
    w, x, y, z = q
    roll  = np.arctan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
    pitch = np.arcsin(np.clip(2*(w*y - z*x), -1, 1))
    yaw   = np.arctan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
    return roll, pitch, yaw

def quat_to_rotmat(q):
    w, x, y, z = q
    return np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - z*w),     2*(x*z + y*w)],
        [2*(x*y + z*w),     1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w),     2*(y*z + x*w),     1 - 2*(x*x + y*y)]
    ])

# ========================================================
# Data loading
# ========================================================

def load_data(path):
    try:
        df = pd.read_csv(path, comment='#', sep=None, engine='python')
    except Exception:
        # Fallback for space-delimited files that sep=None fails on
        df = pd.read_csv(path, delim_whitespace=True, comment='#')

    cols = {c.lower(): c for c in df.columns}

    def find_col(names):
        for n in names:
            if n in cols:
                return cols[n]
        return None

    t  = find_col(['timestamp', 'time', 't'])
    ax = find_col(['ax', 'accel_x', 'a_x'])
    ay = find_col(['ay', 'accel_y', 'a_y'])
    az = find_col(['az', 'accel_z', 'a_z'])
    gx = find_col(['gx', 'gyro_x', 'g_x'])
    gy = find_col(['gy', 'gyro_y', 'g_y'])
    gz = find_col(['gz', 'gyro_z', 'g_z'])

    if None in (t, ax, ay, az, gx, gy, gz):
        raise ValueError("Missing one or more required columns (timestamp, ax, ay, az, gx, gy, gz).")

    data = pd.DataFrame({
        't':  df[t].astype(float),
        'ax': df[ax].astype(float),
        'ay': df[ay].astype(float),
        'az': df[az].astype(float),
        'gx': df[gx].astype(float),
        'gy': df[gy].astype(float),
        'gz': df[gz].astype(float)
    })

    # Convert timestamp from ms to s if necessary
    if data['t'].median() > 1e5:
        data['t'] /= 1000.0
    
    # Ensure data is sorted by time
    data = data.sort_values('t').reset_index(drop=True)
    return data


# ========================================================
# Geometry helpers
# ========================================================

def cube_vertices(size=1.0):
    s = size / 2
    return np.array([
        [-s, -s, -s], [ s, -s, -s], [ s,  s, -s], [-s,  s, -s],
        [-s, -s,  s], [ s, -s,  s], [ s,  s,  s], [-s,  s,  s]
    ])

CUBE_FACES = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
              (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4)]

def transform_vertices(verts, R, trans=np.zeros(3)):
    return verts.dot(R.T) + trans

# ========================================================
# Simulation + rendering
# ========================================================

def simulate_and_render(data, output_path, fps=30, cube_size=0.4, rod_length=0.8):
    t = data['t'].values
    dt = np.median(np.diff(t))
    gyro_rad = np.deg2rad(data[['gx', 'gy', 'gz']].values)
    accel = data[['ax', 'ay', 'az']].values

    # --- Run AHRS algorithm ---
    madgwick = MadgwickAHRS(sample_period=dt, beta=0.1)
    quats = []
    for g, a in zip(gyro_rad, accel):
        madgwick.update_imu(g, a)
        quats.append(madgwick.quaternion())
    quats = np.array(quats)
    eulers = np.array([quat_to_euler(q) for q in quats])
    
    # --- Setup plots ---
    fig = plt.figure(figsize=(16, 9))
    ax3d = fig.add_subplot(1, 2, 1, projection='3d')
    ax2d = fig.add_subplot(1, 2, 2)

    # 3D plot setup
    ax3d.set_xlim(-1, 1); ax3d.set_ylim(-1, 1); ax3d.set_zlim(-1, 1)
    ax3d.set_box_aspect([1, 1, 1])

    # 2D plot setup
    ax2d.set_xlim(t[0], t[-1])
    ax2d.set_xlabel('Time (s)')

    accel_mag = np.linalg.norm(accel, axis=1)
    gyro_mag = np.linalg.norm(gyro_rad, axis=1)
    ax2d.plot(t, accel_mag, label='|a| (raw)')
    ax2d.plot(t, gyro_mag, label='|ω| (rad/s)', linestyle='--')
    ax2d.plot(t, eulers[:, 0], label='roll (rad)', linestyle='-.')
    ax2d.plot(t, eulers[:, 1], label='pitch (rad)', linestyle=':')
    ax2d.plot(t, eulers[:, 2], label='yaw (rad)')
    ax2d.legend(fontsize='small')

    # --- Render animation ---
    writer = animation.FFMpegWriter(fps=fps, bitrate=6000)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cube = cube_vertices(cube_size)

    total_frames = int((t[-1] - t[0]) * fps)
    print(f"Rendering {total_frames} frames...")

    with writer.saving(fig, output_path, dpi=150):
        for ti in tqdm(np.linspace(t[0], t[-1], total_frames)):
            # Find closest data index
            idx = np.searchsorted(t, ti)
            q = quats[min(idx, len(quats) - 1)]
            R = quat_to_rotmat(q)
            
            # Get geometry
            verts = transform_vertices(cube, R)
            rod = np.array([[0, 0, 0], [0, 0, rod_length]]).dot(R.T)

            # Draw 3D plot
            ax3d.cla()
            for face in CUBE_FACES:
                quad = verts[list(face)]
                ax3d.add_collection3d(art3d.Poly3DCollection([quad], alpha=0.8))
            ax3d.plot(rod[:, 0], rod[:, 1], rod[:, 2], lw=2.0)
            ax3d.set_xlim(-1, 1); ax3d.set_ylim(-1, 1); ax3d.set_zlim(-1, 1)
            ax3d.set_box_aspect([1, 1, 1])
            ax3d.set_title(f"t={ti:.2f}s")

            # Draw 2D plot vline
            ax2d.axvline(ti, color='k', lw=0.6, alpha=0.6)
            writer.grab_frame(facecolor=fig.get_facecolor())
            ax2d.lines.pop()  # remove old vline

    print(f"✅ Simulation complete: {output_path}")


# ========================================================
# CLI + defaults
# ========================================================

def parse_args():
    p = argparse.ArgumentParser(description="Generate payload flight simulation MP4 from MPU6050 log.")
    p.add_argument('--input', '-i', help='Path to MPU6050 log file.')
    p.add_argument('--output', '-o', default='output/payload_simulation.mp4', help='Output MP4 path.')
    p.add_argument('--fps', type=int, default=30)
    return p.parse_args()

def main():
    args = parse_args()

    if not args.input:
        default_path = 'src/logger/data/MPU6050.txt'
        if os.path.exists(default_path):
            args.input = default_path
            print(f"No --input specified, using default: {default_path}")
        else:
            print("Error: No input provided and default file not found.")
            sys.exit(1)

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    print("\n=== Payload Flight Vector Simulation ===")
    print(f"Input : {args.input}")
    print(f"Output: {args.output}")
    print(f"FPS   : {args.fps}")
    print("========================================\n")

    data = load_data(args.input)
    simulate_and_render(data, args.output, fps=args.fps)


if __name__ == '__main__':
    main()
