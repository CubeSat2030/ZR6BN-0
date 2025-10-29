#!/usr/bin/env python3
"""
sensor_fusion.py
- Runs Madgwick AHRS on processed CSV
- Produces orientations (quaternions) and Euler angles
"""
import numpy as np
import pandas as pd
from math import sqrt

INPUT = "../data/processed_mpu.csv"
OUTPUT = "../data/fused.csv"

# Madgwick parameters
BETA = 0.1  # tuning param (0.1 is reasonable; increase to trust gyro more)
def normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

def madgwick_update(q, gx, gy, gz, ax, ay, az, dt, beta=BETA):
    # q = [w, x, y, z]
    # convert gyro to rad/s already expected
    # Implementation following standard Madgwick algorithm (simplified)
    qw, qx, qy, qz = q
    # Normalise accelerometer measurement
    a = np.array([ax, ay, az])
    if np.linalg.norm(a) == 0:
        return q  # no accel
    a = a / np.linalg.norm(a)
    # Auxiliary variables
    _2qw = 2.0 * qw
    _2qx = 2.0 * qx
    _2qy = 2.0 * qy
    _2qz = 2.0 * qz
    # Reference direction of Earth's gravitational field
    # Gradient descent algorithm corrective step (approx).
    # Compute estimated direction of gravity
    vx = _2qx * qz - _2qw * qy
    vy = _2qw * qx + _2qy * qz
    vz = qw*qw - qx*qx - qy*qy + qz*qz
    # Error is cross product between estimated and measured gravity direction
    ex = (a[1]*vz - a[2]*vy)
    ey = (a[2]*vx - a[0]*vz)
    ez = (a[0]*vy - a[1]*vx)
    # Apply feedback
    gx = gx + beta * ex
    gy = gy + beta * ey
    gz = gz + beta * ez
    # Integrate rate of change of quaternion
    qDot_w = -0.5*( qx*gx + qy*gy + qz*gz )
    qDot_x =  0.5*( qw*gx + qy*gz - qz*gy )
    qDot_y =  0.5*( qw*gy - qx*gz + qz*gx )
    qDot_z =  0.5*( qw*gz + qx*gy - qy*gx )
    # Integrate
    qw += qDot_w * dt
    qx += qDot_x * dt
    qy += qDot_y * dt
    qz += qDot_z * dt
    q = np.array([qw, qx, qy, qz])
    q = q / np.linalg.norm(q)
    return q

def quat_to_euler(q):
    qw, qx, qy, qz = q
    # roll (x-axis rotation)
    sinr_cosp = 2*(qw*qx + qy*qz)
    cosr_cosp = 1 - 2*(qx*qx + qy*qy)
    roll = np.arctan2(sinr_cosp, cosr_cosp)
    # pitch (y-axis)
    sinp = 2*(qw*qy - qz*qx)
    if abs(sinp) >= 1:
        pitch = np.sign(sinp) * (np.pi/2)
    else:
        pitch = np.arcsin(sinp)
    # yaw (z-axis)
    siny_cosp = 2*(qw*qz + qx*qy)
    cosy_cosp = 1 - 2*(qy*qy + qz*qz)
    yaw = np.arctan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw

def run():
    df = pd.read_csv(INPUT)
    n = len(df)
    qs = np.zeros((n,4))
    eulers = np.zeros((n,3))
    # initial quaternion align accel to gravity vector
    q = np.array([1.0, 0.0, 0.0, 0.0])
    for i in range(n):
        if i == 0:
            dt = 1.0 / 50.0
        else:
            dt = df['time'].iloc[i] - df['time'].iloc[i-1]
            if dt <= 0:
                dt = 1e-3
        gx = np.deg2rad(df['gx'].iloc[i]) if 'gx' in df.columns else 0.0
        gy = np.deg2rad(df['gy'].iloc[i]) if 'gy' in df.columns else 0.0
        gz = np.deg2rad(df['gz'].iloc[i]) if 'gz' in df.columns else 0.0
        ax = df['ax'].iloc[i]
        ay = df['ay'].iloc[i]
        az = df['az'].iloc[i]
        q = madgwick_update(q, gx, gy, gz, ax, ay, az, dt)
        qs[i,:] = q
        eulers[i,:] = quat_to_euler(q)
    out = df.copy()
    out['qw'], out['qx'], out['qy'], out['qz'] = qs[:,0], qs[:,1], qs[:,2], qs[:,3]
    out['roll'], out['pitch'], out['yaw'] = eulers[:,0], eulers[:,1], eulers[:,2]
    out.to_csv(OUTPUT, index=False)
    print(f"Fused -> {OUTPUT} ({len(out)} rows)")

if __name__ == "__main__":
    run()
