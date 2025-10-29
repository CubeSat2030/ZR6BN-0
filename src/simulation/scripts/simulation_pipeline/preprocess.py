#!/usr/bin/env python3
"""
preprocess.py
---------------------------------
Robust preprocessing for MPU6050 flight data.

Reads:  src/logger/data/MPU6050.txt
Outputs: src/simulation/output/data/preprocessed.csv

Features:
- Handles mixed delimiters (space, tab, comma, semicolon)
- Ignores bad lines automatically
- Cleans extra quotes
- Normalizes acceleration to m/s²
"""

import pandas as pd
from pathlib import Path

INPUT = Path("src/logger/data/MPU6050.txt")
OUTPUT = Path("src/simulation/output/data/preprocessed.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

EXPECTED_COLS = ["timestamp", "ax", "ay", "az", "gx", "gy", "gz"]

def preprocess():
    try:
        # Attempt to read with flexible delimiters and skip bad lines
        df = pd.read_csv(
            INPUT,
            sep=r"[,\s;]+",  # comma, semicolon, or any whitespace
            engine="python",
            header=None,
            names=EXPECTED_COLS,
            on_bad_lines="skip",
            quotechar='"'
        )

        # Drop rows where timestamp is missing
        df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

        # Convert timestamp to float or datetime
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", origin="unix")
        except:
            df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])

        # Normalize acceleration if values look like g (~1)
        if df[["ax","ay","az"]].abs().mean().mean() < 5:
            df[["ax","ay","az"]] *= 9.80665

        df.to_csv(OUTPUT, index=False)
        print(f"[✓] Preprocessed data saved to {OUTPUT} ({len(df)} rows)")

    except Exception as e:
        print(f"[❌] Failed to preprocess {INPUT}: {e}")

if __name__ == "__main__":
    preprocess()
