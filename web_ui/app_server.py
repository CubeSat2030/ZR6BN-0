import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
from flask import Flask, render_template, jsonify, send_from_directory, abort

# --- Configuration ---
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger"
PLOT_DIR = SRC_DIR / "plotter"
SIM_DIR = SRC_DIR / "simulation" / "scripts"
CHARTS_DIR = PLOT_DIR / "charts"
VIDEOS_DIR = PLOT_DIR / "videos" 
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

# Ensure directories exist
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

# --- Global State ---
RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()

SCRIPTS_CONFIG = {
    "main": {
        "title": "Flight Controller (main.py)",
        "log_script": BASE_DIR / "main.py",
        "is_main_controller": True
    },
    "dht": {
        "title": "CPU temp Logger",
        "log_script": LOG_DIR / "cpu_logger.py",
        "plot_script": PLOT_DIR / "cpu_plotter.py",
        "chart_file": "cpu_chart.svg"
    },
    "mpu": {
        "title": "MPU-6050 Logger",
        "log_script": LOG_DIR / "mpu6050_logger.py",
        "plot_script": PLOT_DIR / "mpu6050_plotter.py",
        "chart_file": "mpu_chart.svg"
    },
    "simulation": {
        "title": "Payload Flight Simulation",
        "sim_script": SIM_DIR / "payload_flight_simulation.py",
        "video_file": "BACAR13_stable_replay.mp4" # Pre-existing video
    },
    "sound": {
        "title": "Sound Logger",
        "log_script": LOG_DIR / "sound_logger.py",
        "plot_script": PLOT_DIR / "sound_plotter.py",
        "chart_file": "sound_chart.svg"
    }
}

@app.route("/")
def index():
    # Fix: Convert PosixPath to strings for JSON safety
    serializable_config = {}
    for key, config in SCRIPTS_CONFIG.items():
        if not config.get('is_main_controller'):
            serializable_config[key] = {
                "title": str(config["title"]),
                "chart_file": str(config.get("chart_file")) if config.get("chart_file") else None,
                "video_file": str(config.get("video_file")) if config.get("video_file") else None
            }
    return render_template("dashboard.html", scripts_config=serializable_config)

@app.route("/api/status")
def api_status():
    status = {}
    with PROCESS_LOCK:
        for name, config in SCRIPTS_CONFIG.items():
            is_running = name in RUNNING_PROCESSES and RUNNING_PROCESSES[name].poll() is None
            status[name] = {
                "running": is_running,
                "chart_file": str(config.get("chart_file")) if config.get("chart_file") else None
            }
    return jsonify(status)

@app.route("/video/<path:filename>")
def get_video_display(filename):
    # conditional=True allows Range requests (streaming) to save 500MB RAM
    return send_from_directory(VIDEOS_DIR, filename, mimetype='video/mp4', conditional=True)

@app.route("/chart/<path:filename>")
def get_chart_display(filename):
    return send_from_directory(CHARTS_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
