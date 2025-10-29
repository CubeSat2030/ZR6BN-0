#!/usr/bin/env python3
"""
simulation_master.py
---------------------------------
Central orchestrator for the HAB Payload Flight Simulation Pipeline.

Stages:
    1. preprocess.py        → Clean and normalize raw MPU6050 data
    2. sensor_fusion.py     → Compute orientation quaternions
    3. trajectory.py        → Integrate motion into 3D trajectory
    4. render_vectors.py    → Render cinematic replay with control vectors

All progress and errors are logged to console and simulation_master.log
"""

import subprocess
import sys
import time
import logging
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
PIPELINE_DIR = Path("src/simulation/scripts/simulation_pipeline")
LOG_FILE = Path("simulation_master.log")

STAGES = [
    ("Preprocessing raw MPU6050 data", "preprocess.py"),
    ("Fusing sensor data (orientation)", "sensor_fusion.py"),
    ("Computing trajectory", "trajectory.py"),
    ("Rendering 3D control vector simulation", "render_vectors.py"),
]

# ─────────────────────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ─────────────────────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────────────────────
def run_stage(name: str, script_name: str) -> bool:
    """Run a single pipeline stage script and capture its output."""
    script_path = PIPELINE_DIR / script_name
    logging.info(f"🚀 Starting stage: {name}")
    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True
        )

        duration = time.time() - start_time
        logging.info(f"✅ Completed {name} in {duration:.2f} seconds")

        if result.stdout.strip():
            logging.info(f"↳ STDOUT:\n{result.stdout.strip()}")

        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Stage failed: {name}")
        logging.error(f"↳ STDOUT:\n{e.stdout.strip()}")
        logging.error(f"↳ STDERR:\n{e.stderr.strip()}")
        return False

    except Exception as ex:
        logging.exception(f"Unexpected error in stage {name}: {ex}")
        return False


# ─────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────
def run_pipeline():
    logging.info("🛰️  HAB Payload Flight Simulation — Simulation Start")
    mission_start = time.time()

    for description, script in STAGES:
        success = run_stage(description, script)
        if not success:
            logging.warning(f"⚠️  Retrying {description} after 3 seconds...")
            time.sleep(3)
            if not run_stage(description, script):
                logging.error(f"🚨 Simulation aborted due to failure in: {description}")
                break

    total_time = time.time() - mission_start
    logging.info(f"🏁 Simulation pipeline completed in {total_time/60:.2f} minutes.")
    logging.info(f"📄 Log saved to {LOG_FILE.resolve()}")

if __name__ == "__main__":
    run_pipeline()
