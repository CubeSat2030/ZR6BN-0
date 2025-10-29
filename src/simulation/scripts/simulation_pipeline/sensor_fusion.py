#!/usr/bin/env python3
"""
sensor_fusion.py
---------------------------------
Robust sensor fusion for MPU6050 data with guaranteed quaternion shape.
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
    df = df.dropna(subset=["timestamp","ax","ay","az","gx","gy","gz"]).reset_index(drop=True)

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

    # Initialize quaternion (identity)
    q = R.identity()
    orientations = []

    for i in range(len(df)):
        if i == 0:
            # First row → identity quaternion
            orientations.append(q.as_quat())
            continue

        dt = (df.timestamp[i] - df.timestamp[i-1]).total_seconds()
        if dt <= 0:
            # Zero or negative dt → repeat last quaternion
            orientations.append(orientations[-1])
            continue

        # Read gyro and accel
        gx, gy, gz = df.loc[i, ["gx","gy","gz"]].values.astype(float)
        ax, ay, az = df.loc[i, ["ax","ay","az"]].values.astype(float)

        # Convert gyro to radians/sec
        gyro_rate = np.array([gx, gy, gz]) * np.pi / 180
        delta_angle = gyro_rate * dt
        delta_rot = R.from_rotvec(delta_angle)

        # Update quaternion
        q = q * delta_rot
        orientations.append(q.as_quat())

    # Ensure orientations array is 2D (N,4)
    q_arr = np.array(orientations)
    if q_arr.ndim == 1 or q_arr.shape[1] != 4:
        print("[⚠] Quaternion array shape invalid, fixing...")
        q_arr = np.vstack([o if len(o)==4 else [1,0,0,0] for o in orientations])

    # Save to CSV
    out_df = pd.DataFrame({
        "timestamp": df["timestamp"].values,
        "qx": q_arr[:,0],
        "qy": q_arr[:,1],
        "qz": q_arr[:,2],
        "qw": q_arr[:,3]
    })
    out_df.to_csv(OUTPUT, index=False)
    print(f"[✓] Orientation data saved to {OUTPUT} ({len(out_df)} rows)")

if __name__ == "__main__":
    run_sensor_fusion()
