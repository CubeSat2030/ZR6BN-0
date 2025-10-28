#!/usr/bin/env python3
"""
main.py — HAB Mission Orchestrator (Post-Flight, Read-Only Logger Data)

Purpose:
    Runs the full post-flight simulation pipeline without ever modifying
    the original MPU6050 sensor log (read-only flight archive).

Pipeline:
    1. Verify logger data (read-only)
    2. Invoke simulation pipeline (simulation_main.py)
    3. Render replay

Usage:
    python main.py --fps 10 --force
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# ───────────────────────────────────────────────
# PATHS (read-only and writable directories)
# ───────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
LOGGER_DATA = SRC / "logger" / "data"
RAW_INPUT = LOGGER_DATA / "MPU6050.txt"

SIM_SCRIPTS = SRC / "simulation" / "scripts"
SIMULATION_MAIN = SIM_SCRIPTS / "simulation_main.py"

MEDIA = SRC / "media"
OUTPUT = MEDIA / "output"
VIDEO_OUT = OUTPUT / "video" / "BACAR13_flight_replay.mp4"

# ───────────────────────────────────────────────
# LOGGING
# ───────────────────────────────────────────────
logging.basicConfig(
    filename=ROOT / "mission_master.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(message)s", "%H:%M:%S")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

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
    if not RAW_INPUT.exists():
        logging.error(f"❌ Flight data not found: {RAW_INPUT}")
        sys.exit(1)

    # Make sure the file is read-only
    try:
        if os.access(RAW_INPUT, os.W_OK):
            logging.warning(f"⚠️ {RAW_INPUT.name} appears writable — locking it down.")
            RAW_INPUT.chmod(0o444)
        logging.info(f"🛰️  Verified read-only flight log: {RAW_INPUT.name}")
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
