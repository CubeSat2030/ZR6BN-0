#!/usr/bin/env python3
"""
trajectory.py
- Uses fused.csv (quaternions) to rotate accel to world frame and integrate velocity/position.
- Adds simple drag term for stability.
- Exports positions and a short-term ballistic 'future' trajectory for each frame.
"""
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

INPUT = "../data/fused.csv"
OUTPUT = "../data/trajectory.csv"
G = np.array([0, 0, 9.80665])

def quat_rotate_vector(q, v):
    # rotate body vector v to world frame using quaternion q=[w,x,y,z]
    qw,qx,qy,qz = q
    # q * [0,v] * q_conj
    t = 2.0 * np.cross([qx,qy,qz], v)
    v_rot = v + qw * t + np.cross([qx,qy,qz], t)
    return v_rot

def integrate(df, drag_coeff=0.02):
    n = len(df)
    vel = np.zeros((n,3))
    pos = np.zeros((n,3))
    for i in range(1,n):
        dt = df['time'].iloc[i] - df['time'].iloc[i-1]
        if dt <= 0:
            dt = 1e-3
        q = df.loc[i, ['qw','qx','qy','qz']].to_numpy()
        a_body = df.loc[i, ['ax','ay','az']].to_numpy()
        a_world = quat_rotate_vector(q, a_body)
        # subtract gravity
        lin_acc = a_world - G
        # apply simple drag: a_drag = -k * v
        a_drag = -drag_coeff * vel[i-1]
        v_new = vel[i-1] + (lin_acc + a_drag) * dt
        p_new = pos[i-1] + v_new * dt
        vel[i] = v_new
        pos[i] = p_new
    # optional smoothing on position (small window)
    pos[:,2] = savgol_filter(pos[:,2], 51 if n>51 else 5, 3, mode='interp')
    df_out = df.copy()
    df_out[['vx','vy','vz']] = vel
    df_out[['px','py','pz']] = pos
    return df_out

def future_trajectory(px, py, pz, vx, vy, vz, steps=50, dt=0.1):
    # simple ballistic predict (gravity + drag)
    k = 0.02
    traj = []
    p = np.array([px,py,pz], dtype=float)
    v = np.array([vx,vy,vz], dtype=float)
    for _ in range(steps):
        a = np.array([0,0,-9.80665]) - k*v
        v = v + a*dt
        p = p + v*dt
        traj.append(p.copy())
    return np.array(traj)

def main():
    df = pd.read_csv(INPUT)
    df_out = integrate(df)
    # compute short future trajectories for each sample and store only last sample for rendering speed as needed
    # For now store only final future from last sample
    last = df_out.iloc[-1]
    fut = future_trajectory(last.px, last.py, last.pz, last.vx, last.vy, last.vz, steps=200, dt=0.5)
    df_out.to_csv(OUTPUT, index=False)
    print("Trajectory computed ->", OUTPUT)
    # save future separately
    pd.DataFrame(fut, columns=['fx','fy','fz']).to_csv("../out/video/future_last.csv", index=False)

if __name__ == "__main__":
    main()
