#!/usr/bin/env python3
"""
preprocess.py
---------------------------------
Preprocesses MPU6050 data logs for the HAB payload flight simulation.

Reads:  src/logger/data/MPU6050.txt
Outputs: src/simulation/output/data/preprocessed.csv
"""

import pandas as pd
from pathlib import Path

INPUT = Path("src/logger/data/MPU6050.txt")
OUTPUT = Path("src/simulation/output/data/preprocessed.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def preprocess():
    df = pd.read_csv(INPUT, sep=r"\s+|,|;", engine="python", header=None)
    df.columns = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz"]

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", origin="unix", errors="coerce")
    df.dropna(inplace=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Normalize acceleration (g to m/s² if needed)
    if df["ax"].abs().mean() < 5:  
        df[["ax", "ay", "az"]] *= 9.80665

    df.to_csv(OUTPUT, index=False)
    print(f"[✓] Preprocessed data saved to {OUTPUT}")

if __name__ == "__main__":
    preprocess()
