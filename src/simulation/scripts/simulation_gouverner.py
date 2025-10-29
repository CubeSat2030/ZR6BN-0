#!/usr/bin/env python3
"""
project tree:

├── .gitattributes
├── README.md
├── main.py
├── mission_master.log
├── requirements.txt
├── simulation_gouverner.log
├── src/
│   ├── .gitkeeep
│   ├── logger/
│   │   ├── __pycache__/
│   │   │   └── heartbeat.cpython-313.pyc
│   │   ├── calibrate_sound.py
│   │   ├── cpu_logger.py
│   │   ├── data/
│   │   │   ├── CPU_TEMP.txt
│   │   │   ├── LATEST_SENSOR_DATA.json
│   │   │   ├── LATEST_SYSTEM_STATUS.json
│   │   │   ├── MPU6050.txt
│   │   │   ├── sound_data_D0.txt
│   │   │   └── sound_data_D0_backup.txt
│   │   ├── heartbeat.py
│   │   ├── heartbeats/
│   │   │   ├── cpu_logger.json
│   │   │   └── mpu_logger.json
│   │   ├── mpu6050_logger.py
│   │   └── sound_logger.py
│   ├── media/
│   │   ├── .gitkeep
│   │   └── output/
│   │       ├── .gitkeep
│   │       ├── image/
│   │       │   └── .gitkeep
│   │       └── video/
│   │           └── .gitkeep
│   ├── plotter/
│   │   ├── charts/
│   │   │   ├── cpu_chart.svg
│   │   │   ├── cpu_chart_backup.svg
│   │   │   ├── mpu_chart.svg
│   │   │   ├── mpu_chart_backup.svg
│   │   │   └── mpu_phases.svg
│   │   ├── cpu_plotter.py
│   │   ├── mpu6050_plotter.py
│   │   └── sound_plotter.py
│   └── simulation/
│       ├── .gitkeep
│       └── scripts/
│           ├── simulation_gouverner.py
│           └── simulation_pipeline/
│               ├── preprocess.py
│               ├── render.py
│               ├── sensor_fusion.py
│               └── trajectory.py
└── web_ui/
    ├── app_server.py
    └── templates/
        └── dashboard.html


"""
        

# About the script
# simulation_gouverner.py 
# Purpose:
#    Runs the full post-flight simulation pipeline without ever modifying
#    the original MPU6050 sensor log (read-only flight archive)

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path


# =========================================================================
# Paths
# =========================================================================

# =========================================================================
# Paths
# =========================================================================

# --- Configuration ---

# Corrected: Go up three levels to reach the project root directory
# from: [PROJECT_ROOT]/src/simulation/scripts/simulation_gouverner.py
# up 1: [PROJECT_ROOT]/src/simulation/scripts/
# up 2: [PROJECT_ROOT]/src/simulation/
# up 3: [PROJECT_ROOT]/src/
# up 4: [PROJECT_ROOT]/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# SRC_DIR is correctly defined as the 'src' folder inside the project root
SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger" 
DATA_DIR = LOG_DIR / "data" 

# This now resolves correctly to [PROJECT_ROOT]/src/logger/data/MPU6050.txt
DATA_FILE = DATA_DIR / "MPU6050.txt" 

PLOT_DIR = SRC_DIR / "plotter"
SIM_DIR = SRC_DIR / "simulation"
SIMULATION_MAIN = SIM_DIR / "scripts" / "simulation_gouverner.py"
SIMULATION_PIPELINE_DIR = SIM_DIR / "scripts" / "simulation_pipeline"
CHARTS_DIR = PLOT_DIR / "charts" 
OUTPUT = SIM_DIR / "output" # This output path is inside src/simulation/ which seems wrong for a simulation file, but kept as per your original structure
VIDEO_OUT = OUTPUT / "video" / "flight_replay.mp4"
# =========================================================================

# ───────────────────────────────────────────────
# Script  path Config
# ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("simulation_gouverner.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# ───────────────────────────────────────────────
# script paths in simulation_pipeline
# ───────────────────────────────────────────────
PREPROCESS_SCRIPT = SIMULATION_PIPELINE_DIR / "preprocess.py"
FUSION_SCRIPT = SIMULATION_PIPELINE_DIR / "sensor_fusion.py"
RENDER_SCRIPT = SIMULATION_PIPELINE_DIR / "render_simulation.py"
TRAJECTORY_SCRIPT = SIMULATION_PIPELINE_DIR / "trajectory.py"

# ───────────────────────────────────────────────
# UTILITIES
# ───────────────────────────────────────────────
def ensure_dirs():
    """Ensure only output folders are writable."""
    (OUTPUT / "video").mkdir(parents=True, exist_ok=True)
    (OUTPUT / "image").mkdir(parents=True, exist_ok=True)
    logging.info("📁 Verified output directories")


def verify_readonly_source():
    """Confirm MPU6050.txt exists and is read-only."""
    if not DATA_FILE.exists():
        logging.error(f"❌ Flight data not found: {DATA_FILE}")
        sys.exit(1)

    # Make sure the file is read-only
    try:
        if os.access(DATA_FILE, os.W_OK):
            logging.warning(f"⚠️ {DATA_FILE.name} appears writable — locking it down.")
            DATA_FILE.chmod(0o444)
        logging.info(f"🛰️  Verified read-only flight log: {DATA_FILE.name}")
    except Exception as e:
        logging.warning(f"Could not verify file permissions: {e}")


def run_simulation(fps: int, force: bool):
    """Run post-flight simulation pipeline (simulation_main.py)."""
    if not SIMULATION_MAIN.exists():
        logging.error(f"Simulation entrypoint missing: {SIMULATION_MAIN}")
        sys.exit(1)

    env = os.environ.copy()
    env["HAB_SIM_FPS"] = str(fps)
    env["HAB_SIM_FORCE"] = "1" if force else "0"
    env["HAB_FLIGHT_MODE"] = "POST"  # signal downstream modules

    logging.info("🚀 Launching post-flight simulation pipeline...")
    result = subprocess.run([sys.executable, str(SIMULATION_MAIN)], env=env)
    if result.returncode != 0:
        logging.error(f"❌ Simulation pipeline failed (exit {result.returncode})")
        sys.exit(result.returncode)
    logging.info("✅ Simulation pipeline complete")


# ───────────────────────────────────────────────
# MAIN ENTRY
# ───────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="HAB Post-Flight Orchestrator")
    parser.add_argument("--fps", type=int, default=10, help="Render FPS for replay video")
    parser.add_argument("--force", action="store_true", help="Force rerun of derived data")
    parser.add_argument("--skip-sim", action="store_true", help="Skip simulation pipeline")
    args = parser.parse_args()

    ensure_dirs()
    verify_readonly_source()

    if not args.skip_sim:
        run_simulation(args.fps, args.force)
    else:
        logging.info("⏭️  Skipping simulation (--skip-sim)")

    logging.info("🎯 Mission orchestrator complete")
    print(f"\n🎬 Final video: {VIDEO_OUT if VIDEO_OUT.exists() else 'not generated'}")


if __name__ == "__main__":
    main()
