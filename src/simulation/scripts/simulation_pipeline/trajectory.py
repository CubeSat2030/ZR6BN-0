#!/usr/bin/env python3
"""
trajectory.py
---------------------------------
Computes position by integrating linear acceleration, after orientation compensation.

Reads:
    src/simulation/output/data/preprocessed.csv
    src/simulation/output/data/orientation.csv
Outputs:
    src/simulation/output/data/trajectory.csv
"""

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
from pathlib import Path

PREPROCESSED = Path("src/simulation/output/data/preprocessed.csv")
ORIENTATION = Path("src/simulation/output/data/orientation.csv")
OUTPUT = Path("src/simulation/output/data/trajectory.csv")

def integrate_trajectory():
    acc_df = pd.read_csv(PREPROCESSED)
    ori_df = pd.read_csv(ORIENTATION)
    merged = pd.merge_asof(acc_df, ori_df, on="timestamp")

    pos = np.zeros(3)
    vel = np.zeros(3)
    trajectory = []

    for i in range(1, len(merged)):
        dt = (pd.to_datetime(merged.timestamp[i]) - pd.to_datetime(merged.timestamp[i - 1])).total_seconds()
        if dt <= 0:
            continue

        rot = R.from_quat(merged.loc[i, ["qx", "qy", "qz", "qw"]])
        acc_body = merged.loc[i, ["ax", "ay", "az"]].to_numpy()
        acc_world = rot.apply(acc_body)
        acc_world[2] -= 9.80665

        vel += acc_world * dt
        pos += vel * dt

        trajectory.append([merged.timestamp[i], *pos, *vel, *rot.as_euler('xyz', degrees=True), *rot.as_quat()])

    columns = ["timestamp", "px", "py", "pz", "vx", "vy", "vz",
               "roll", "pitch", "yaw", "qx", "qy", "qz", "qw"]
    traj_df = pd.DataFrame(trajectory, columns=columns)
    traj_df.to_csv(OUTPUT, index=False)
    print(f"[✓] Trajectory data saved to {OUTPUT}")

if __name__ == "__main__":
    integrate_trajectory()
