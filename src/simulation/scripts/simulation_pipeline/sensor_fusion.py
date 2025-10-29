#!/usr/bin/env python3
"""
sensor_fusion.py
---------------------------------
Applies a complementary filter to fuse gyro and accel data into orientation quaternions.

Reads:  src/simulation/output/data/preprocessed.csv
Outputs: src/simulation/output/data/orientation.csv
"""

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
from pathlib import Path

INPUT = Path("src/simulation/output/data/preprocessed.csv")
OUTPUT = Path("src/simulation/output/data/orientation.csv")

def complementary_filter(ax, ay, az, gx, gy, gz, dt, alpha=0.98):
    # Gyro integration
    gyro_rate = np.array([gx, gy, gz]) * np.pi / 180
    delta_angle = gyro_rate * dt
    delta_rot = R.from_rotvec(delta_angle)
    return delta_rot

def run_sensor_fusion():
    df = pd.read_csv(INPUT)
    q = R.identity()

    orientations = []
    timestamps = df["timestamp"]
    for i in range(1, len(df)):
        dt = (pd.to_datetime(timestamps[i]) - pd.to_datetime(timestamps[i - 1])).total_seconds()
        if dt <= 0:
            continue

        gx, gy, gz = df.loc[i, ["gx", "gy", "gz"]]
        ax, ay, az = df.loc[i, ["ax", "ay", "az"]]

        delta_rot = complementary_filter(ax, ay, az, gx, gy, gz, dt)
        q = q * delta_rot
        orientations.append(q.as_quat())

    q_arr = np.array(orientations)
    out_df = pd.DataFrame({
        "timestamp": timestamps.iloc[1:].values,
        "qw": q_arr[:, 3],
        "qx": q_arr[:, 0],
        "qy": q_arr[:, 1],
        "qz": q_arr[:, 2]
    })
    out_df.to_csv(OUTPUT, index=False)
    print(f"[✓] Orientation data saved to {OUTPUT}")

if __name__ == "__main__":
    run_sensor_fusion()
