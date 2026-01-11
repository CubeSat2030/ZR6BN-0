import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
import shutil
from flask import Flask, render_template, jsonify, send_from_directory, abort, request

try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(21)
    BUZZER_AVAILABLE = True
except ImportError:
    BUZZER_AVAILABLE = False
    BUZZER = None
except Exception as e:
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

# Data wipe paths
DATA_DIR = LOG_DIR / "data" / "1_preflight"
HEARTBEATS_DIR = LOG_DIR / "heartbeats"
FOOTAGE_DIR = SRC_DIR / "photography" / "footage"

# --- Global State ---
AUTO_START_TIMEOUT = 60
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()
LAST_BEEP_TIME = 0
SOLID_BEEP_START_TIME = None

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()

SCRIPTS_CONFIG = {
    "main": {"title": "Flight Controller (main.py)", "log_script": BASE_DIR / "main.py", "is_main_controller": True},
    "dht": {"title": "CPU temp Logger", "log_script": LOG_DIR / "cpu_logger.py", "plot_script": PLOT_DIR / "cpu_plotter.py", "chart_file": "cpu_chart.svg"},
    "mpu": {"title": "MPU-6050 Logger", "log_script": LOG_DIR / "mpu6050_logger.py", "plot_script": PLOT_DIR / "mpu6050_plotter.py", "chart_file": "mpu_chart.svg"},
    "simulation": {"title": "Payload Flight Simulation", "sim_script": SIM_DIR / "payload_flight_simulation.py", "video_file": "BACAR13_stable_replay.mp4"},
    "sound": {"title": "Sound Logger", "log_script": LOG_DIR / "sound_logger.py", "plot_script": PLOT_DIR / "sound_plotter.py", "chart_file": "sound_chart.svg"}
}

# --- Process Helpers ---
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
            running = False
            pid = None
            if name in RUNNING_PROCESSES:
                if RUNNING_PROCESSES[name].poll() is None:
                    running = True
                    pid = RUNNING_PROCESSES[name].pid
                else: del RUNNING_PROCESSES[name]
            
            key = 'main_controller' if config.get('is_main_controller') else name
            status[key] = {"title": config['title'], "running": running, "pid": pid, "chart_file": config.get('chart_file'), "video_file": config.get('video_file')}
    return status

# --- Routes ---
@app.route("/")
def index():
    serializable_config = {k: v for k, v in SCRIPTS_CONFIG.items() if not v.get('is_main_controller')}
    return render_template("dashboard.html", scripts_config=serializable_config)

@app.route("/api/status")
def api_status(): return jsonify(get_status())

@app.route('/api/simulation/<name>', methods=['POST'])
def api_simulation_generate(name):
    if is_main_controller_active(): return jsonify({"success": False, "message": "Controller active."}), 403
    
    config = SCRIPTS_CONFIG.get(name)
    script_path = str(config['sim_script'])
    try:
        # Non-blocking run for simulation to prevent web timeout
        subprocess.Popen([sys.executable, script_path], cwd=str(BASE_DIR))
        return jsonify({"success": True, "message": "Simulation started. Refresh when complete."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/video/<path:filename>")
def get_video_display(filename):
    if ".." in filename or "/" in filename: abort(400)
    # conditional=True is critical for 500MB RAM to stream rather than load
    return send_from_directory(VIDEOS_DIR, filename, mimetype='video/mp4', conditional=True)

@app.route("/chart/<path:filename>")
def get_chart_display(filename):
    return send_from_directory(CHARTS_DIR, filename)

@app.route('/api/script/<name>/<action>', methods=['POST'])
def api_script_control(name, action):
    # Standard start/stop logic... (omitted for brevity, keep your original implementation here)
    return jsonify({"success": True, "message": f"{action} executed"})

# --- Main ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
