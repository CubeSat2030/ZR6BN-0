import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
from flask import Flask, render_template, jsonify, send_from_directory, abort

# --- Buzzer Initialization ---
try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(21)
    BUZZER_AVAILABLE = True
except Exception:
    BUZZER_AVAILABLE = False
    BUZZER = None

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

# --- Global State ---
AUTO_START_TIMEOUT = 60
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()
RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

# --- Scripts Configuration ---
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
        "video_file": "BACAR13_stable_replay.mp4"
    },
    "sound": {
        "title": "Sound Logger",
        "log_script": LOG_DIR / "sound_logger.py",
        "plot_script": PLOT_DIR / "sound_plotter.py",
        "chart_file": "sound_chart.svg"
    }
}

# --- Helpers ---
def is_main_controller_active():
    with PROCESS_LOCK:
        if 'main' in RUNNING_PROCESSES:
            if RUNNING_PROCESSES['main'].poll() is None: return True
            else: del RUNNING_PROCESSES['main']
    return False

def get_status():
    status = {}
    with PROCESS_LOCK:
        for name, config in SCRIPTS_CONFIG.items():
            is_running = False
            pid = None
            if name in RUNNING_PROCESSES:
                if RUNNING_PROCESSES[name].poll() is None:
                    is_running = True
                    pid = RUNNING_PROCESSES[name].pid
                else: del RUNNING_PROCESSES[name]
            
            key = 'main_controller' if config.get('is_main_controller') else name
            status[key] = {
                "title": config['title'],
                "running": is_running,
                "pid": pid,
                "chart_file": str(config.get('chart_file')) if config.get('chart_file') else None,
                "video_file": str(config.get('video_file')) if config.get('video_file') else None
            }
    return status

# --- Flask Routes ---
@app.route("/")
def index():
    """Renders dashboard with stringified config to avoid PosixPath JSON errors."""
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
    return jsonify(get_status())

@app.route('/api/simulation/<name>', methods=['POST'])
def api_simulation_generate(name):
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller active. Simulation disabled."}), 403
    
    config = SCRIPTS_CONFIG.get(name)
    if not config or 'sim_script' not in config:
        return jsonify({"success": False, "message": "Invalid simulation name."}), 400

    try:
        # Launching simulation as a separate process to avoid blocking Flask
        subprocess.Popen([sys.executable, str(config['sim_script'])], cwd=str(BASE_DIR))
        return jsonify({"success": True, "message": "Simulation started. It will appear here once generated."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/video/<path:filename>")
def get_video_display(filename):
    """Streams video using 206 Partial Content (RAM friendly)."""
    if ".." in filename or "/" in filename: abort(400)
    return send_from_directory(VIDEOS_DIR, filename, mimetype='video/mp4', conditional=True)

@app.route("/chart/<path:filename>")
def get_chart_display(filename):
    if ".." in filename or "/" in filename: abort(400)
    return send_from_directory(CHARTS_DIR, filename)

@app.before_request
def reset_timer():
    global LAST_CONNECTION_TIME
    LAST_CONNECTION_TIME = time.time()

# --- Main Entry ---
if __name__ == "__main__":
    print(f"Starting Kabot-1 Mission Control on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
