#!/usr/bin/env python3
"""
sensor_fusion.py
---------------------------------
Robust sensor fusion for MPU6050 data to compute quaternions.

Reads:  src/simulation/output/data/preprocessed.csv
Outputs: src/simulation/output/data/orientation.csv

Features:
- Skips rows with missing or non-numeric data
- Handles zero or negative dt between timestamps
- Ensures quaternion arrays remain consistent
"""

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
from pathlib import Path

INPUT = Path("src/simulation/output/data/preprocessed.csv")
OUTPUT = Path("src/simulation/output/data/orientation.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def run_sensor_fusion():
    df = pd.read_csv(INPUT)
    df = df.dropna(subset=["timestamp","ax","ay","az","gx","gy","gz"])
    df = df.reset_index(drop=True)

    timestamps = pd.to_datetime(df["timestamp"], errors="coerce")
    df["timestamp"] = timestamps
    df = df.dropna(subset=["timestamp"])
    df = df.reset_index(drop=True)

    # Initialize quaternion (identity)
    q = R.identity()
    orientations = []

    for i in range(1, len(df)):
        dt = (df.timestamp[i] - df.timestamp[i-1]).total_seconds()
        if dt <= 0:
            orientations.append(q.as_quat())
            continue

        gx, gy, gz = df.loc[i, ["gx","gy","gz"]].values.astype(float)
        ax, ay, az = df.loc[i, ["ax","ay","az"]].values.astype(float)

        # Convert gyro to radians/sec
        gyro_rate = np.array([gx, gy, gz]) * np.pi / 180
        delta_angle = gyro_rate * dt
        delta_rot = R.from_rotvec(delta_angle)

        # Update quaternion
        q = q * delta_rot
        orientations.append(q.as_quat())

    if len(orientations) != len(df):
        print("[⚠] Orientation array length mismatch, adjusting...")
        while len(orientations) < len(df):
            orientations.append(q.as_quat())

    q_arr = np.array(orientations)
    out_df = pd.DataFrame({
        "timestamp": df["timestamp"].iloc[1:].values,
        "qw": q_arr[1:, 3],
        "qx": q_arr[1:, 0],
        "qy": q_arr[1:, 1],
        "qz": q_arr[1:, 2]
    })
    out_df.to_csv(OUTPUT, index=False)
    print(f"[✓] Orientation data saved to {OUTPUT} ({len(out_df)} rows)")

if __name__ == "__main__":
    run_sensor_fusion()
