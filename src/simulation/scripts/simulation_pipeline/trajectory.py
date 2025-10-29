#!/usr/bin/env python3
"""
trajectory.py
---------------------------------
Compute payload position by integrating accelerometer data, 
compensated by orientation quaternions.

Reads:
    src/simulation/output/data/preprocessed.csv
    src/simulation/output/data/orientation.csv
Outputs:
    src/simulation/output/data/trajectory.csv

Features:
- Skips bad/missing rows
- Handles zero/negative dt
- Ensures quaternion and accel arrays are aligned
"""

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
from pathlib import Path

PREPROCESSED = Path("src/simulation/output/data/preprocessed.csv")
ORIENTATION = Path("src/simulation/output/data/orientation.csv")
OUTPUT = Path("src/simulation/output/data/trajectory.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def integrate_trajectory():
    # Load data
    acc_df = pd.read_csv(PREPROCESSED).dropna().reset_index(drop=True)
    ori_df = pd.read_csv(ORIENTATION).dropna().reset_index(drop=True)

    # Align by timestamp using nearest merge
    df = pd.merge_asof(acc_df, ori_df, on="timestamp", direction="nearest", tolerance=pd.Timedelta("100ms"))
    df = df.dropna(subset=["qx","qy","qz","qw","ax","ay","az"]).reset_index(drop=True)

    pos = np.zeros(3)
    vel = np.zeros(3)
    trajectory = []

    for i in range(len(df)):
        if i == 0:
            trajectory.append([df.timestamp[i], *pos, *vel, 0,0,0, df.qx[i], df.qy[i], df.qz[i], df.qw[i]])
            continue

        dt = (pd.to_datetime(df.timestamp[i]) - pd.to_datetime(df.timestamp[i-1])).total_seconds()
        if dt <= 0:
            # Zero or negative dt → repeat last pos/vel
            trajectory.append([df.timestamp[i], *pos, *vel, 0,0,0, df.qx[i], df.qy[i], df.qz[i], df.qw[i]])
            continue

        # Orientation
        rot = R.from_quat([df.qx[i], df.qy[i], df.qz[i], df.qw[i]])

        # Acceleration in world frame
        acc_body = df.loc[i, ["ax","ay","az"]].to_numpy().astype(float)
        acc_world = rot.apply(acc_body)
        acc_world[2] -= 9.80665  # gravity compensation

        # Integrate velocity and position
        vel += acc_world * dt
        pos += vel * dt

        roll, pitch, yaw = rot.as_euler('xyz', degrees=True)
        trajectory.append([df.timestamp[i], *pos, *vel, roll, pitch, yaw, df.qx[i], df.qy[i], df.qz[i], df.qw[i]])

    columns = ["timestamp", "px","py","pz","vx","vy","vz",
               "roll","pitch","yaw","qx","qy","qz","qw"]
    traj_df = pd.DataFrame(trajectory, columns=columns)
    traj_df.to_csv(OUTPUT, index=False)
    print(f"[✓] Trajectory data saved to {OUTPUT} ({len(traj_df)} rows)")

if __name__ == "__main__":
    integrate_trajectory()
