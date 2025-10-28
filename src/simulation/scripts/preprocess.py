#!/usr/bin/env python3
"""
preprocess.py
- Loads raw CSV (timestamp, ax,ay,az,gx,gy,gz)
- Converts units, resamples to uniform rate, calibrates biases
- Outputs processed CSV for fusion
"""
import numpy as np
import pandas as pd
from scipy.signal import medfilt

INPUT = "../data/raw_mpu.csv"
OUTPUT = "../data/processed_mpu.csv"
TARGET_HZ = 10.0  # keep as your sample rate (10 Hz)

def load_and_clean(path):
    df = pd.read_csv(path)
    # Expect columns: time, ax, ay, az, gx, gy, gz
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    # Try to detect time column
    if 'time' not in df.columns:
        if 'timestamp' in df.columns:
            df.rename(columns={'timestamp':'time'}, inplace=True)
        else:
            raise ValueError("CSV must contain 'time' or 'timestamp' column")
    # Ensure monotonic time in seconds
    t = df['time'].to_numpy()
    # if timestamps are unix ms, detect large values
    if np.nanmean(t) > 1e9:
        # assume ms
        df['time'] = df['time'] / 1000.0
    return df

def calibrate(df):
    # Simple static bias estimation: take first 2 seconds as zero motion
    df = df.copy()
    start_window = df['time'] <= df['time'].iloc[0] + 2.0
    if start_window.sum() < 5:
        start_window = df.index[:min(len(df), 20)]
    biases = {}
    for c in ['gx','gy','gz','ax','ay','az']:
        if c in df.columns:
            biases[c] = df.loc[start_window, c].mean()
    # remove gyro bias; accelerometer bias removal is trickier due to gravity.
    for g in ['gx','gy','gz']:
        if g in df.columns:
            df[g] = df[g] - biases[g]
    # For accel, subtract mean and then re-scale so gravity magnitude ~9.80665 in first window
    if all(k in df.columns for k in ('ax','ay','az')):
        ax0 = df.loc[start_window, ['ax','ay','az']].mean().values
        gmag = np.linalg.norm(ax0)
        if gmag > 0:
            scale = 9.80665 / gmag
            df[['ax','ay','az']] = df[['ax','ay','az']] * scale
    # Optional median filter to remove spikes
    for c in ['ax','ay','az','gx','gy','gz']:
        if c in df.columns:
            df[c] = medfilt(df[c], kernel_size=3)
    return df

def resample(df, hz=TARGET_HZ):
    # Use pandas time index
    df = df.copy()
    t0 = df['time'].iloc[0]
    df['tidx'] = pd.to_datetime((df['time'] - t0), unit='s')
    df = df.set_index('tidx')
    new_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq=pd.Timedelta(seconds=1.0/hz))
    df_res = df.reindex(df.index.union(new_idx)).interpolate(method='time').reindex(new_idx)
    df_res['time'] = (df_res.index - df_res.index[0]).total_seconds() + t0
    # drop tidx index restore simple index
    return df_res.reset_index(drop=True)

def main():
    df = load_and_clean(INPUT)
    df = calibrate(df)
    df = resample(df, TARGET_HZ)
    df.to_csv(OUTPUT, index=False)
    print(f"Processed -> {OUTPUT} | {len(df)} samples @ {TARGET_HZ} Hz")

if __name__ == "__main__":
    main()
