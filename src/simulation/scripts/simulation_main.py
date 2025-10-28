#!/usr/bin/env python3
"""
main.py — Mission Orchestrator for HAB Payload Flight Vector Simulation

Runs the full post-flight simulation pipeline:
    1. Preprocess   → Clean & resample MPU6050 raw logs
    2. SensorFusion → Combine accel + gyro → attitude (Euler/quaternion)
    3. Trajectory   → Reconstruct flight vector from attitude + acceleration
    4. Render       → Generate cinematic replay MP4

Usage:
    python main.py --force --fps 10
    python main.py --skip-render  # useful for quick data tests
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path
import shutil

# ────────────────────────────────────────────────────────────────
# PATH SETUP (matches your structure)
# ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SIM = SRC / "simulation"
SCRIPTS = SIM / "scripts"
LOGGER_DATA = SRC / "logger" / "data"
MEDIA = SRC / "media"
OUTPUT = MEDIA / "output"
VIDEO_OUT = OUTPUT / "video" / "BACAR13_flight_replay.mp4"

# Expected input
RAW_INPUT = LOGGER_DATA / "MPU6050.txt"

# Stage outputs
PROCESSED = SCRIPTS / "processed.csv"
FUSED = SCRIPTS / "fused.csv"
TRAJECTORY = SCRIPTS / "trajectory.csv"

# Script paths
PREPROCESS = SCRIPTS / "preprocess.py"
FUSION = SCRIPTS / "sensor_fusion.py"
TRAJECTORY_SCRIPT = SCRIPTS / "trajectory.py"
RENDER = SCRIPTS / "render.py"

# ────────────────────────────────────────────────────────────────
# LOGGING
# ────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="mission_master.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(message)s", "%H:%M:%S")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


# ────────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────────
def run_stage(name: str, cmd: list[str], skip: bool, output_file: Path | None, force: bool):
    if skip:
        logging.info(f"⏭️  Skipping {name} stage (--skip flag)")
        return

    if output_file and output_file.exists() and not force:
        logging.info(f"✅ {name} output exists: {output_file.name} (use --force to regenerate)")
        return

    logging.info(f"🚀 Running {name} stage...")
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        logging.error(f"❌ {name} failed (exit {result.returncode})")
        sys.exit(result.returncode)
    logging.info(f"✅ {name} complete")


def ensure_dirs():
    for p in [MEDIA, OUTPUT / "video", OUTPUT / "image"]:
        p.mkdir(parents=True, exist_ok=True)
    logging.info("📁 Directory check complete")


# ────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="HAB Payload Flight Vector Simulation")
    parser.add_argument("--fps", type=int, default=10, help="Output video FPS (default: 10)")
    parser.add_argument("--force", action="store_true", help="Force rerun all stages")
    parser.add_argument("--skip-preprocess", action="store_true")
    parser.add_argument("--skip-fusion", action="store_true")
    parser.add_argument("--skip-trajectory", action="store_true")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="Path to ffmpeg binary")
    args = parser.parse_args()

    ensure_dirs()

    if not RAW_INPUT.exists():
        logging.error(f"Raw input not found: {RAW_INPUT}")
        sys.exit(1)

    # Pass fps as environment variable for render.py
    env = os.environ.copy()
    env["HAB_SIM_FPS"] = str(args.fps)

    # ──────────────────────
    # PIPELINE EXECUTION
    # ──────────────────────
    run_stage(
        "Preprocess",
        [sys.executable, str(PREPROCESS)],
        args.skip_preprocess,
        PROCESSED,
        args.force,
    )

    run_stage(
        "Sensor Fusion",
        [sys.executable, str(FUSION)],
        args.skip_fusion,
        FUSED,
        args.force,
    )

    run_stage(
        "Trajectory Reconstruction",
        [sys.executable, str(TRAJECTORY_SCRIPT)],
        args.skip_trajectory,
        TRAJECTORY,
        args.force,
    )

    run_stage(
        "Render",
        [sys.executable, str(RENDER)],
        args.skip_render,
        VIDEO_OUT,
        args.force,
    )

    logging.info("🎯 Mission simulation pipeline complete")
    print(f"\nFinal video: {VIDEO_OUT if VIDEO_OUT.exists() else 'not generated'}")


# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
