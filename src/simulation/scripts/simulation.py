#!/usr/bin/env python3
"""
payload_simulation_from_mpu6050.py

Single-file simulation:
 - Loads MPU6050 post-flight log (timestamp, ax, ay, az, gx, gy, gz)
 - Runs Madgwick AHRS to estimate orientation
 - Renders split-screen: left = 3D payload (cube + rod), right = telemetry charts
 - Exports an MP4 file using matplotlib.animation.FFMpegWriter (requires ffmpeg)

Usage:
    python payload_simulation_from_mpu6050.py \
        --input src/logger/data/MPU6050.txt \
        --output output/payload_simulation.mp4 \
        --fps 30 --scale 1.0

Notes:
 - Assumes MPU6050 gyro units are degrees/second and accel in g or m/s^2 (script normalizes accel).
 - If accel is in g, it still works (norm is used).
 - If your file has different column names, edit load_data() accordingly.
"""

import os
import sys
import argparse
from dataclasses import dataclass
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')   # ensure non-interactive backend for file output
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from math import sin, cos
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------
# Madgwick AHRS (Python impl)
# ---------------------------
# Small, self-contained Madgwick filter (alpha-based update)
# Reference: S. O. H. Madgwick's algorithm simplified for accel+gyro
class MadgwickAHRS:
    def __init__(self, sample_period=1/256.0, beta=0.1):
        self.sample_period = sample_period
        self.beta = beta
        # quaternion representing orientation: q = [w, x, y, z]
        self.q = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)

    @staticmethod
    def _normalize(v):
        n = np.linalg.norm(v)
        if n == 0:
            return v
        return v / n

    def update_imu(self, gyro, accel):
        """
        Update quaternion using gyroscope (rad/s) and accelerometer (m/s^2 or g).
        gyro: np.array([gx, gy, gz]) in radians/sec
        accel: np.array([ax, ay, az]) (not necessarily normalized)
        """
        q1, q2, q3, q4 = self.q  # q = [w, x, y, z]

        # Normalize accelerometer measurement
        if np.linalg.norm(accel) == 0:
            return
        ax, ay, az = MadgwickAHRS._normalize(accel)

        # Auxiliary variables
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q4 = 2.0 * q4
        _4q1 = 4.0 * q1
        _4q2 = 4.0 * q2
        _4q3 = 4.0 * q3
        _8q2 = 8.0 * q2
        _8q3 = 8.0 * q3
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3
        q4q4 = q4 * q4

        # Gradient descent algorithm corrective step
        s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
        s2 = _4q2 * q4q4 - _2q4 * ax + 4.0 * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az
        s3 = 4.0 * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az
        s4 = 4.0 * q2q2 * q4 - _2q2 * ax + 4.0 * q3q3 * q4 - _2q3 * ay

        s = np.array([s1, s2, s3, s4], dtype=float)
        s = MadgwickAHRS._normalize(s)

        # Rate of change of quaternion from gyroscope
        gx, gy, gz = gyro
        q_dot_omega = 0.5 * np.array([
            -q2 * gx - q3 * gy - q4 * gz,
             q1 * gx + q3 * gz - q4 * gy,
             q1 * gy - q2 * gz + q4 * gx,
             q1 * gz + q2 * gy - q3 * gx
        ], dtype=float)

        # Apply feedback step
        q_dot = q_dot_omega - self.beta * s

        # Integrate to yield quaternion
        self.q += q_dot * self.sample_period
        self.q = MadgwickAHRS._normalize(self.q)

    def quaternion(self):
        return self.q.copy()

# ---------------------------
# Utility functions
# ---------------------------
def quat_to_euler(q):
    # q: [w, x, y, z]
    w, x, y, z = q
    # roll (x-axis rotation)
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = np.arctan2(t0, t1)
    # pitch (y-axis rotation)
    t2 = +2.0 * (w * y - z * x)
    t2 = np.clip(t2, -1.0, 1.0)
    pitch = np.arcsin(t2)
    # yaw (z-axis rotation)
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = np.arctan2(t3, t4)
    return roll, pitch, yaw  # in radians

def quat_to_rotmat(q):
    # returns 3x3 rotation matrix
    w, x, y, z = q
    R = np.array([
        [1 - 2*(y*y+z*z),     2*(x*y - z*w),     2*(x*z + y*w)],
        [    2*(x*y + z*w), 1 - 2*(x*x+z*z),     2*(y*z - x*w)],
        [    2*(x*z - y*w),     2*(y*z + x*w), 1 - 2*(x*x + y*y)]
    ], dtype=float)
    return R

# ---------------------------
# Data loading
# ---------------------------
def load_data(path):
    """
    Load MPU6050 log.
    Expected CSV-like with header or whitespace-separated columns.
    Columns expected (any order but must contain):
        timestamp, ax, ay, az, gx, gy, gz
    timestamp: seconds (float) OR integer ms (script will normalize to seconds)
    gyro assumed degrees/sec (will be converted to rad/s)
    accel can be in g or m/s^2 (we use normalized accel so absolute units don't matter)
    """
    # try pandas read_csv with flexible separators
    df = None
    try:
        df = pd.read_csv(path, comment='#', sep=None, engine='python')
    except Exception:
        # fallback: whitespace separator
        df = pd.read_csv(path, delim_whitespace=True, comment='#')

    # normalize column names
    cols = {c.lower(): c for c in df.columns}
    # detect timestamp-like column
    ts_col = None
    for possible in ['timestamp', 'time', 't', 'ts', 'unix_time', 'milliseconds']:
        if possible in cols:
            ts_col = cols[possible]
            break
    if ts_col is None:
        # might be first column w/o header
        ts_col = df.columns[0]

    # find accel and gyro
    def find_col(possible_names):
        for name in possible_names:
            if name in cols:
                return cols[name]
        return None

    ax = find_col(['ax', 'accel_x', 'acc_x', 'accx', 'a_x'])
    ay = find_col(['ay', 'accel_y', 'acc_y', 'accy', 'a_y'])
    az = find_col(['az', 'accel_z', 'acc_z', 'accz', 'a_z'])
    gx = find_col(['gx', 'gyro_x', 'gyr_x', 'g_x'])
    gy = find_col(['gy', 'gyro_y', 'gyr_y', 'g_y'])
    gz = find_col(['gz', 'gyro_z', 'gyr_z', 'g_z'])

    if None in (ax, ay, az, gx, gy, gz):
        raise ValueError("Couldn't find accelerometer/gyro columns automatically. Columns found: "
                         + ", ".join(df.columns))

    data = pd.DataFrame({
        't': df[ts_col].astype(float),
        'ax': df[ax].astype(float),
        'ay': df[ay].astype(float),
        'az': df[az].astype(float),
        'gx': df[gx].astype(float),
        'gy': df[gy].astype(float),
        'gz': df[gz].astype(float),
    })

    # if timestamps look like ms (large numbers), convert to seconds
    if data['t'].median() > 1e5:
        data['t'] = data['t'] / 1000.0

    # ensure monotonic time
    data = data.sort_values('t').reset_index(drop=True)
    # drop exact-duplicate timestamps (rare)
    data = data.loc[data['t'].diff().fillna(1) != 0].reset_index(drop=True)
    return data

# ---------------------------
# Rendering utilities
# ---------------------------
def cube_vertices(size=1.0):
    s = size / 2.0
    # 8 vertices of cube centered at origin
    return np.array([
        [-s, -s, -s],
        [ s, -s, -s],
        [ s,  s, -s],
        [-s,  s, -s],
        [-s, -s,  s],
        [ s, -s,  s],
        [ s,  s,  s],
        [-s,  s,  s],
    ], dtype=float)

CUBE_FACES = [
    (0,1,2,3),
    (4,5,6,7),
    (0,1,5,4),
    (2,3,7,6),
    (1,2,6,5),
    (0,3,7,4)
]

def transform_vertices(verts, R, translation=np.zeros(3), scale=1.0):
    # apply rotation, scaling, translation
    v = verts * scale
    v_rot = v.dot(R.T) + translation
    return v_rot

# ---------------------------
# Main simulation
# ---------------------------
def simulate_and_render(data, output_path, fps=30, scale=1.0, cube_size=0.4,
                        rod_length=0.8, writer_bitrate=6000):
    # compute sample periods from data (we will compute orientation at each data sample)
    times = data['t'].values
    n_samples = len(times)
    # Construct sampling rate: use average dt
    dts = np.diff(times)
    if len(dts) == 0:
        raise ValueError("Insufficient data samples.")
    median_dt = float(np.median(dts))
    # We'll render at fps frames per second and step through data using interpolation
    total_duration = times[-1] - times[0]
    n_frames = int(np.ceil(total_duration * fps))
    if n_frames < 1:
        n_frames = 1

    print(f"Data samples: {n_samples}, duration: {total_duration:.2f}s, output frames: {n_frames}, fps: {fps}")

    # Prepare Madgwick: use sample period based on median dt (but we integrate per sample)
    madgwick = MadgwickAHRS(sample_period=median_dt, beta=0.1)

    # Precompute quaternion / euler at each data sample
    quaternions = np.zeros((n_samples, 4), dtype=float)
    eulers = np.zeros((n_samples, 3), dtype=float)
    accel_mag = np.zeros(n_samples, dtype=float)
    gyro_mag = np.zeros(n_samples, dtype=float)

    # Convert gyro to rad/s (assume deg/s in file) -> rad/s
    gyro_deg = data[['gx','gy','gz']].values.astype(float)
    gyro_rad = np.deg2rad(gyro_deg)

    accel = data[['ax','ay','az']].values.astype(float)

    # Iterate through samples and run Madgwick
    for i in range(n_samples):
        gx, gy, gz = gyro_rad[i]
        ax, ay, az = accel[i]
        accel_mag[i] = np.linalg.norm([ax, ay, az])
        gyro_mag[i] = np.linalg.norm([gx, gy, gz])
        madgwick.update_imu(np.array([gx, gy, gz], dtype=float),
                            np.array([ax, ay, az], dtype=float))
        q = madgwick.quaternion()
        quaternions[i] = q
        eulers[i] = np.array(quat_to_euler(q))  # radians

    # Interpolation helpers for per-frame sampling
    def interp_array(arr, t_query):
        # arr: (N, *) array indexed by times
        return np.vstack([np.interp(t_query, times, arr[:, j]) for j in range(arr.shape[1])]).T if arr.ndim == 2 else np.interp(t_query, times, arr)

    # Prepare plotting: split-screen
    fig = plt.figure(figsize=(16, 9))
    ax_left = fig.add_subplot(1, 2, 1, projection='3d')
    ax_right = fig.add_subplot(1, 2, 2)

    # Setup left axes (3D)
    lim = 1.2 * (cube_size + rod_length)
    ax_left.set_xlim3d(-lim, lim)
    ax_left.set_ylim3d(-lim, lim)
    ax_left.set_zlim3d(-lim, lim)
    ax_left.set_box_aspect([1,1,1])
    ax_left.set_title("3D Payload View")
    ax_left.set_xticks([])
    ax_left.set_yticks([])
    ax_left.set_zticks([])

    # Setup right axes (telemetry)
    ax_right.set_title("Telemetry (Accel mag, Gyro mag, Euler angles)")
    ax_right.set_xlabel("Time (s)")
    ax_right.grid(True)

    # telemetry lines placeholders
    t0 = times[0]
    times_frames = np.linspace(t0, times[-1], n_frames)
    # Precompute telemetry interpolation arrays for faster per-frame plotting
    accel_interp = np.interp(times_frames, times, accel_mag)
    gyro_interp = np.interp(times_frames, times, gyro_mag)
    euler_interp = np.vstack([np.interp(times_frames, times, eulers[:, j]) for j in range(3)]).T

    # telemetry plot limits
    ax_right.clear()
    ax_right.set_xlim(times_frames[0], times_frames[-1])
    ax_right.set_ylim(-4.0, 4.0)  # will adjust dynamically below with margins

    # Build telemetry traces (we'll update data via set_data)
    telemetry_ax1 = ax_right.twinx()
    p_accel, = ax_right.plot([], [], lw=1.2, label='accel|a| (raw)')
    p_gyro, = telemetry_ax1.plot([], [], lw=1.0, label='gyro|ω| (rad/s)', linestyle='--')

    # Euler angles as separate small subplot inside right? We'll plot them below telemetry as lines:
    # To simplify, plot Euler angles normalized to [-pi, pi] on same left y-axis scaled
    p_roll, = ax_right.plot([], [], lw=0.8, label='roll (rad)', linestyle='-.')
    p_pitch, = ax_right.plot([], [], lw=0.8, label='pitch (rad)', linestyle=':')
    p_yaw, = ax_right.plot([], [], lw=0.8, label='yaw (rad)', linestyle='-')

    # Legends
    lines = [p_accel, p_gyro, p_roll, p_pitch, p_yaw]
    labels = [l.get_label() for l in lines]
    ax_right.legend(lines, labels, loc='upper right', fontsize='small')

    # Prepare video writer
    FFMpegWriter = animation.writers['ffmpeg']
    metadata = dict(title='Payload Simulation', artist='simulation-script')
    writer = FFMpegWriter(fps=fps, metadata=metadata, bitrate=writer_bitrate)

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    # Precompute cube vertices
    base_verts = cube_vertices(size=cube_size)

    # We'll step frames and draw them, writing each frame via writer.grab_frame()
    print("Starting frame render and video write...")
    with writer.saving(fig, output_path, dpi=150):
        # Use tqdm to show progress on console
        for fi, t in enumerate(tqdm(times_frames, desc="Frames")):
            # Sample nearest orientation from computed quaternions via interpolation of quaternion components
            # Simple interp: linear interp of quaternion components then normalization
            q_interp = np.array([np.interp(t, times, quaternions[:, j]) for j in range(4)])
            q_interp = q_interp / np.linalg.norm(q_interp)
            R = quat_to_rotmat(q_interp)

            # Transform cube and rod
            cube_world = transform_vertices(base_verts, R, translation=np.array([0,0,0]), scale=1.0)
            # rod: a line from cube center to +Z in body coordinates length rod_length
            rod_pts_body = np.array([[0,0,0],[0,0,rod_length]])
            rod_world = rod_pts_body.dot(R.T)

            # Clear and redraw 3D
            ax_left.cla()
            ax_left.set_title(f"3D Payload View — t={t - t0:.2f}s")
            ax_left.set_xlim3d(-lim, lim)
            ax_left.set_ylim3d(-lim, lim)
            ax_left.set_zlim3d(-lim, lim)
            ax_left.set_box_aspect([1,1,1])
            # draw cube faces
            for face in CUBE_FACES:
                quad = cube_world[list(face)]
                ax_left.add_collection3d(matplotlib.art3d.Poly3DCollection([quad], alpha=0.9, linewidths=0.3))

            # draw rod
            ax_left.plot(rod_world[:,0], rod_world[:,1], rod_world[:,2], lw=2.0)

            # optionally add a ground plane / atmosphere fade based on normalized altitude proxy (we don't have altitude)
            # We'll simulate a fade: tNormalized = (t - t0) / total_duration
            tnorm = np.clip((t - t0) / (times[-1] - times[0] + 1e-9), 0.0, 1.0)
            # tint background
            bg_color = (0.05 + 0.35 * (1 - tnorm), 0.05 + 0.4 * (1 - tnorm), 0.15 + 0.5 * (1 - tnorm))
            ax_left.set_facecolor(bg_color)

            # Telemetry side: update plot lines up to current frame
            xdata = times_frames[:fi+1] - t0
            accel_y = accel_interp[:fi+1]
            gyro_y = gyro_interp[:fi+1]
            euler_y = euler_interp[:fi+1]  # roll/pitch/yaw

            p_accel.set_data(xdata, accel_y)
            p_gyro.set_data(xdata, gyro_y)
            p_roll.set_data(xdata, euler_y[:,0])
            p_pitch.set_data(xdata, euler_y[:,1])
            p_yaw.set_data(xdata, euler_y[:,2])

            # update telemetry axis limits adaptively
            ax_right.relim()
            ax_right.autoscale_view()
            telemetry_ax1.relim()
            telemetry_ax1.autoscale_view()

            ax_right.set_xlim(0, times_frames[-1] - t0)

            # Draw current vertical time line
            # remove previous vlines by clearing - we'll draw anew each frame
            ax_right.collections.clear()  # removing vlines
            ax_right.axvline(x=(t - t0), color='k', lw=0.6, alpha=0.6)

            # small text overlays
            roll, pitch, yaw = quat_to_euler(q_interp)
            deg = lambda r: r * 180.0 / np.pi
            ax_right.text(0.02, 0.95, f"roll={deg(roll):.1f}°, pitch={deg(pitch):.1f}°, yaw={deg(yaw):.1f}°",
                          transform=ax_right.transAxes, fontsize=8, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.6))

            # finalize and write frame
            writer.grab_frame(facecolor=fig.get_facecolor())

    print("Finished. Output saved to:", output_path)

# ---------------------------
# CLI and main
# ---------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Generate payload flight simulation MP4 from MPU6050 log.")
    p.add_argument('--input', '-i', required=True, help='Path to MPU6050 log file (CSV or whitespace sep).')
    p.add_argument('--output', '-o', default='payload_simulation.mp4', help='Output MP4 path.')
    p.add_argument('--fps', type=int, default=30, help='Output video frames per second.')
    p.add_argument('--scale', type=float, default=1.0, help='Scene scale factor.')
    p.add_argument('--cube', type=float, default=0.4, help='Cube size (m).')
    p.add_argument('--rod', type=float, default=0.8, help='Rod length (m).')
    p.add_argument('--bitrate', type=int, default=6000, help='FFmpeg bitrate (kbit/s).')
    return p.parse_args()

def main():
    args = parse_args()

    # load
    print("Loading data from:", args.input)
    data = load_data(args.input)
    if len(data) < 2:
        print("Error: Need at least 2 samples.")
        sys.exit(1)

    # simulate + render
    simulate_and_render(data, args.output, fps=args.fps, scale=args.scale,
                        cube_size=args.cube, rod_length=args.rod, writer_bitrate=args.bitrate)

if __name__ == '__main__':
    main()
