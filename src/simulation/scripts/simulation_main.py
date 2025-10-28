#!/usr/bin/env python3
"""
simulation_main.py - Orchestrator for the HAB payload simulation pipeline.

Features:
 - Runs preprocess -> sensor_fusion -> trajectory -> render in order
 - Resume support: will skip steps if expected outputs already exist (use --force to re-run)
 - CLI flags for skipping stages, controlling FPS, and changing sample rate
 - Basic logging and error handling
 - Runs the existing scripts via subprocess (keeps each stage isolated)
"""

from __future__ import annotations
import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path
import datetime
import logging

# default paths - relative to repository root (adjust if needed)
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "src" / "simulation" / "scripts"
DATA_DIR = ROOT / "src" / "logger"/ "data"
OUT_DIR = ROOT / "src" / "media" / "output" / "video"

DEFAULT_RAW = DATA_DIR / "raw_mpu.csv"
PROCESSED = DATA_DIR / "processed_mpu.csv"
FUSED = DATA_DIR / "fused.csv"
TRAJ = DATA_DIR / "trajectory.csv"
FUTURE_LAST = OUT_DIR / "future_last.csv"
VIDEO_OUT = OUT_DIR / "hab_sim.mp4"

# script filenames (assumes the scripts exist in scripts/)
PREPROCESS_SCRIPT = SCRIPTS_DIR / "preprocess.py"
FUSION_SCRIPT = SCRIPTS_DIR / "sensor_fusion.py"
TRAJECTORY_SCRIPT = SCRIPTS_DIR / "trajectory.py"
RENDER_SCRIPT = SCRIPTS_DIR / "render.py"

LOGFMT = "%(asctime)s %(levelname)s: %(message)s"


def run_cmd(cmd: list[str], env=None, cwd: Path | None = None):
    """Run a command and stream its output; raise on error."""
    logging.info("RUN: %s", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, cwd=cwd)
    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            sys.stdout.write(line)
    except KeyboardInterrupt:
        proc.terminate()
        raise
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"Command failed ({ret}): {' '.join(cmd)}")


def check_scripts_exist():
    missing = []
    for p in (PREPROCESS_SCRIPT, FUSION_SCRIPT, TRAJECTORY_SCRIPT, RENDER_SCRIPT):
        if not p.exists():
            missing.append(p)
    if missing:
        logging.error("Missing required scripts: %s", ", ".join(str(x) for x in missing))
        raise FileNotFoundError("Required scripts missing in scripts/ folder.")


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_args():
    p = argparse.ArgumentParser(description="HAB sim pipeline orchestrator")
    p.add_argument("--raw", type=Path, default=DEFAULT_RAW, help="Path to raw MPU CSV")
    p.add_argument("--fps", type=int, default=10, help="Output video FPS (should match sample rate to keep real-time length)")
    p.add_argument("--hz", type=float, default=10.0, help="Target resample frequency (used by preprocess.py)")
    p.add_argument("--force", action="store_true", help="Re-run all stages even if outputs exist")
    p.add_argument("--skip-preprocess", action="store_true")
    p.add_argument("--skip-fusion", action="store_true")
    p.add_argument("--skip-trajectory", action="store_true")
    p.add_argument("--skip-render", action="store_true")
    p.add_argument("--ffmpeg-path", default="ffmpeg", help="Path to ffmpeg binary (render step will use it)")
    p.add_argument("--venv-python", default=sys.executable, help="Python interpreter to run scripts with (default: current)")
    return p.parse_args()


def stage_preprocess(raw: Path, force: bool, py_exec: str, hz: float):
    logging.info("STAGE: preprocess")
    if not raw.exists():
        raise FileNotFoundError(f"Raw input not found: {raw}")
    if PROCESSED.exists() and not force:
        logging.info("Processed file already exists at %s (use --force to overwrite). Skipping.", PROCESSED)
        return
    cmd = [py_exec, str(PREPROCESS_SCRIPT)]
    # Allow passing TARGET_HZ by environment variable to avoid editing script - preprocess.py reads TARGET_HZ constant,
    # so if you want to change it without modifying the script, we could write a small wrapper. For now we rely on script constant.
    run_cmd(cmd)


def stage_fusion(force: bool, py_exec: str):
    logging.info("STAGE: sensor fusion")
    if not PROCESSED.exists():
        raise FileNotFoundError(f"Processed file missing: {PROCESSED}. Run preprocess first.")
    if FUSED.exists() and not force:
        logging.info("Fused file already exists at %s (use --force to overwrite). Skipping.", FUSED)
        return
    cmd = [py_exec, str(FUSION_SCRIPT)]
    run_cmd(cmd)


def stage_trajectory(force: bool, py_exec: str):
    logging.info("STAGE: trajectory")
    if not FUSED.exists():
        raise FileNotFoundError(f"Fused file missing: {FUSED}. Run sensor_fusion first.")
    if TRAJ.exists() and not force:
        logging.info("Trajectory file already exists at %s (use --force to overwrite). Skipping.", TRAJ)
        return
    cmd = [py_exec, str(TRAJECTORY_SCRIPT)]
    run_cmd(cmd)


def stage_render(force: bool, py_exec: str, ffmpeg_path: str, fps: int):
    logging.info("STAGE: render")
    # render.py will produce frames and assemble via ffmpeg; it expects ffmpeg in PATH.
    # We ensure ffmpeg exists
    if shutil.which(ffmpeg_path) is None:
        logging.warning("ffmpeg not found at '%s' on PATH. render.py will likely fail when assembling.", ffmpeg_path)
    if VIDEO_OUT.exists() and not force:
        logging.info("Video already exists at %s (use --force to overwrite). Skipping render.", VIDEO_OUT)
        return
    # We supply FPS via environment variable so render.py can optionally read it.
    env = os.environ.copy()
    env["HAB_SIM_FPS"] = str(fps)
    # Call render script with the given python interpreter
    cmd = [py_exec, str(RENDER_SCRIPT)]
    run_cmd(cmd, env=env)


def main():
    args = parse_args()
    # basic logging
    logging.basicConfig(level=logging.INFO, format=LOGFMT)
    logging.info("HAB sim orchestrator starting")
    logging.info("Repo root: %s", ROOT)
    logging.info("Args: %s", vars(args))
    ensure_dirs()
    check_scripts_exist()

    try:
        if not args.skip_preprocess:
            stage_preprocess(args.raw, args.force, args.venv_python, args.hz)
        else:
            logging.info("Skipping preprocess stage (--skip-preprocess).")

        if not args.skip_fusion:
            stage_fusion(args.force, args.venv_python)
        else:
            logging.info("Skipping fusion stage (--skip-fusion).")

        if not args.skip_trajectory:
            stage_trajectory(args.force, args.venv_python)
        else:
            logging.info("Skipping trajectory stage (--skip-trajectory).")

        if not args.skip_render:
            stage_render(args.force, args.venv_python, args.ffmpeg_path, args.fps)
        else:
            logging.info("Skipping render stage (--skip-render).")

    except Exception as e:
        logging.exception("Pipeline failed: %s", e)
        sys.exit(2)

    logging.info("Pipeline finished successfully.")
    logging.info("Video output (if render ran): %s", VIDEO_OUT)
    # print helpful next-steps
    print("\nNext steps / checks:")
    print(f" - Processed CSV: {PROCESSED.exists()}")
    print(f" - Fused CSV:     {FUSED.exists()}")
    print(f" - Trajectory CSV:{TRAJ.exists()}")
    print(f" - Video:         {VIDEO_OUT.exists()} -> {VIDEO_OUT if VIDEO_OUT.exists() else 'not created'}")


if __name__ == "__main__":
    main()
