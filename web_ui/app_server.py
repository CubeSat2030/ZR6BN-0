# =========================================================================
# Kabot-1 Mission Control Dashboard Server - THREAD-SAFE VERSION WITH VIDEO FIXES
# =========================================================================
# Updated: January 2025 - Video serving improvements
# - Proper video export directory
# - Explicit video/mp4 MIME type
# - Filename-only in config
# - Better logging & 404 handling
# =========================================================================

import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
import shutil
from flask import Flask, render_template, jsonify, send_from_directory, abort

try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(21)
    BUZZER_AVAILABLE = True
except ImportError:
    print("[WARNING] gpiozero or RPi.GPIO not available. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False
except Exception as e:
    print(f"[WARNING] Could not initialize Buzzer on GPIO 21: {e}. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False

# --- Configuration ---
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MAIN_CONTROLLER_SCRIPT = BASE_DIR / "main.py"
SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger"
PLOT_DIR = SRC_DIR / "plotter"
SIM_DIR = SRC_DIR / "simulation" / "scripts"
CHARTS_DIR = PLOT_DIR / "charts"
VIDEOS_DIR = PLOT_DIR / "videos"                     # ← VIDEO EXPORT DIRECTORY
EXPORT_DIR = SRC_DIR / "plotter"
HEARTBEATS_DIR = LOG_DIR / "heartbeats"
FOOTAGE_DIR = SRC_DIR / "photography" / "footage"

# Ensure directories exist
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# --- Global State ---
AUTO_START_TIMEOUT = 60  # Seconds
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()
LAST_BEEP_TIME = 0
SOLID_BEEP_START_TIME = None

# --- Flask App ---
app = Flask(__name__, template_folder=str(BASE_DIR / "web_ui" / "templates"))

PROCESS_LOCK = threading.Lock()
RUNNING_PROCESSES = {}

SCRIPTS_CONFIG = {
    "main": {
        "title": "Flight Controller (main.py)",
        "log_script": MAIN_CONTROLLER_SCRIPT,
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
        "video_file": "BACAR13_stable_replay.mp4",           # ← Just filename!
    },
    "sound": {
        "title": "Sound Logger",
        "log_script": LOG_DIR / "sound_logger.py",
        "plot_script": PLOT_DIR / "sound_plotter.py",
        "chart_file": "sound_chart.svg"
    }
}

# =========================================================================
# SYSTEM PROCESS CONTROL (THREAD-SAFE)
# =========================================================================

def is_main_controller_active():
    with PROCESS_LOCK:
        if 'main' in RUNNING_PROCESSES:
            if RUNNING_PROCESSES['main'].poll() is None:
                return True
            else:
                del RUNNING_PROCESSES['main']
        return False

def get_status():
    status = {}
    with PROCESS_LOCK:
        for name in SCRIPTS_CONFIG:
            is_running = False
            pid = None
            if name in RUNNING_PROCESSES:
                if RUNNING_PROCESSES[name].poll() is None:
                    is_running = True
                    pid = RUNNING_PROCESSES[name].pid
                else:
                    del RUNNING_PROCESSES[name]
            state = {'running': is_running, 'pid': pid}
            
            if SCRIPTS_CONFIG[name].get('is_main_controller', False):
                status['main_controller'] = {
                    "running": state['running'],
                    "title": SCRIPTS_CONFIG[name]['title'],
                    "pid": state['pid']
                }
            else:
                status[name] = {
                    "title": SCRIPTS_CONFIG[name]['title'],
                    "running": state['running'],
                    "pid": state['pid'],
                    "chart_file": SCRIPTS_CONFIG[name].get('chart_file')
                }
    return status

def start_script(name):
    if name != 'main' and is_main_controller_active():
        return False, "Flight Controller is running. Manual loggers disabled."
    if name not in SCRIPTS_CONFIG:
        return False, "Unknown script."

    config = SCRIPTS_CONFIG[name]
    script_key = 'log_script' if 'log_script' in config else ('sim_script' if 'sim_script' in config else None)
    if not script_key:
        return False, f"No script path for '{name}'"

    script_path = str(config[script_key])

    with PROCESS_LOCK:
        if name in RUNNING_PROCESSES and RUNNING_PROCESSES[name].poll() is None:
            return False, f"{config['title']} already running (PID: {RUNNING_PROCESSES[name].pid})"

        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(BASE_DIR)
            )
            RUNNING_PROCESSES[name] = process
            return True, f"Started {config['title']} (PID: {process.pid})"
        except Exception as e:
            return False, f"Failed to start {name}: {str(e)}"

def stop_script(name):
    if name != 'main' and is_main_controller_active():
        return False, "Cannot stop manual script while Flight Controller is active."
    with PROCESS_LOCK:
        if name not in RUNNING_PROCESSES or RUNNING_PROCESSES[name].poll() is not None:
            return False, f"{name} is not running."
        try:
            os.killpg(os.getpgid(RUNNING_PROCESSES[name].pid), signal.SIGTERM)
            time.sleep(0.5)
            del RUNNING_PROCESSES[name]
            return True, f"Stopped {SCRIPTS_CONFIG.get(name, {}).get('title', name)}"
        except Exception:
            if name in RUNNING_PROCESSES:
                del RUNNING_PROCESSES[name]
            return False, f"Failed to stop {name}"

def run_plotter(name):
    if is_main_controller_active():
        return False, "Cannot generate charts while Flight Controller is active."
    if name not in SCRIPTS_CONFIG or 'plot_script' not in SCRIPTS_CONFIG[name]:
        return False, "Not a valid plotter script."
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['plot_script'])
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0 and (CHARTS_DIR / config['chart_file']).exists():
            return True, f"Chart generated: {config['chart_file']}"
        else:
            return False, f"Plotting failed: {result.stderr or 'exit code ' + str(result.returncode)}"
    except Exception as e:
        return False, f"Plotter error: {str(e)}"

def run_simulation(name):
    if is_main_controller_active():
        return False, "Cannot run simulation while Flight Controller is active."
    if name not in SCRIPTS_CONFIG or 'sim_script' not in SCRIPTS_CONFIG[name]:
        return False, "Not a valid simulation script."

    config = SCRIPTS_CONFIG[name]
    script_path = str(config['sim_script'])
    video_filename = config['video_file']
    video_path = VIDEOS_DIR / video_filename

    print(f"[SIM] Starting simulation → expected output: {video_path}")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=28800,  # 8 hours max
            cwd=str(BASE_DIR)
        )

        if result.returncode == 0 and video_path.exists():
            size_mb = video_path.stat().st_size / (1024 * 1024)
            print(f"[SIM SUCCESS] Video created: {video_path} ({size_mb:.1f} MB)")
            return True, f"Video generated successfully: {video_filename}"
        else:
            error = result.stderr.strip() or f"exit code {result.returncode}"
            print(f"[SIM ERROR] {error}")
            return False, f"Simulation failed: {error}"
    except subprocess.TimeoutExpired:
        return False, "Simulation timed out (8h limit)"
    except Exception as e:
        print(f"[SIM EXCEPTION] {str(e)}")
        return False, f"Failed to run simulation: {str(e)}"

def wipe_data_and_charts():
    if is_main_controller_active():
        return False, "Cannot wipe data while Flight Controller is active."
    
    success = True
    total_deleted = 0

    patterns = [
        (LOG_DIR.glob("*.txt"), "logger txt files"),
        (LOG_DIR / "data" / "1_preflight").glob("*.*"), 
        (HEARTBEATS_DIR.glob("*.*")),
        (CHARTS_DIR.glob("*.*")),
        (VIDEOS_DIR.glob("*.*")),
        (FOOTAGE_DIR.rglob("*.*"))
    ]

    for pattern, desc in patterns:
        try:
            count = 0
            for item in pattern:
                if item.is_file():
                    item.unlink()
                    count += 1
            total_deleted += count
            if count > 0:
                print(f"[WIPE] Deleted {count} files from {desc}")
        except Exception as e:
            success = False
            print(f"[WIPE ERROR] {desc}: {e}")

    if success:
        return True, f"Wiped {total_deleted} files successfully."
    return False, "Wipe completed with errors - check logs."

# =========================================================================
# BUZZER & AUTO-START (unchanged)
# =========================================================================

def reset_auto_start_timer():
    global LAST_CONNECTION_TIME, SOLID_BEEP_START_TIME
    if BUZZER_AVAILABLE:
        BUZZER.off()
        SOLID_BEEP_START_TIME = None
    if not is_main_controller_active():
        LAST_CONNECTION_TIME = time.time()

# ... (rest of buzzer/countdown functions remain unchanged - omitted for brevity) ...

# =========================================================================
# FLASK ROUTES
# =========================================================================

@app.route("/")
def index():
    serializable_config = {}
    for k, v in SCRIPTS_CONFIG.items():
        if not v.get('is_main_controller'):
            serializable_config[k] = {
                "title": v["title"],
                "chart_file": v.get("chart_file")
            }
    return render_template("dashboard.html", scripts_config=serializable_config)

@app.route("/api/status")
def api_status():
    return jsonify(get_status())

@app.route("/api/script/<name>/<action>", methods=['POST'])
def api_script_control(name, action):
    if name == 'main_controller':
        name = 'main'
    if action == 'start':
        success, msg = start_script(name)
    elif action == 'stop':
        success, msg = stop_script(name)
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400
    return jsonify({"success": success, "message": msg})

@app.route("/api/chart/<name>", methods=['POST'])
def api_chart_generate(name):
    success, msg = run_plotter(name)
    return jsonify({"success": success, "message": msg})

@app.route("/api/simulation/<name>", methods=['POST'])
def api_simulation_generate(name):
    success, msg = run_simulation(name)
    return jsonify({"success": success, "message": msg})

@app.route("/chart/<path:filename>")
def get_chart(filename):
    if ".." in filename or "/" in filename: abort(400)
    return send_from_directory(CHARTS_DIR, filename)

@app.route("/video/<path:filename>")
def get_video(filename):
    """Serve simulation video with proper MIME type"""
    if ".." in filename or "/" in filename:
        abort(400, "Invalid filename")
    
    video_path = VIDEOS_DIR / filename
    
    if not video_path.exists():
        print(f"[VIDEO 404] Not found: {video_path}")
        abort(404, "Simulation video not found")
    
    return send_from_directory(
        VIDEOS_DIR,
        filename,
        mimetype='video/mp4',
        conditional=True
    )

@app.route("/download/chart/<filename>")
def download_chart(filename):
    if ".." in filename or "/" in filename: abort(400)
    path = CHARTS_DIR / filename
    if not path.exists(): abort(404)
    return send_from_directory(CHARTS_DIR, filename, as_attachment=True)

@app.route("/api/control/<action>", methods=['POST'])
def api_system_control(action):
    if action in ['reboot', 'shutdown']:
        cmd = ["sudo", "reboot"] if action == 'reboot' else ["sudo", "shutdown", "now"]
        msg = f"Kabot-1 will {action} momentarily."
        try:
            subprocess.Popen(cmd, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return jsonify({"success": True, "message": msg})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    elif action == 'wipe_data':
        success, msg = wipe_data_and_charts()
        code = 200 if success else (403 if "Flight Controller" in msg else 500)
        return jsonify({"success": success, "message": msg}), code
    return jsonify({"success": False, "message": "Invalid action"}), 400

@app.before_request
def update_connection():
    reset_auto_start_timer()

# =========================================================================
# STARTUP
# =========================================================================

if __name__ == "__main__":
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()

    def cleanup(sig, frame):
        if BUZZER_AVAILABLE:
            BUZZER.off()
        BUZZER_THREAD_STOP.set()
        print("\n[EXIT] Buzzer and countdown stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("Kabot-1 Mission Control Dashboard")
    print(f"Video serving from: {VIDEOS_DIR}")
    print(f"Access: http://0.0.0.0:5000/")
    app.run(host="0.0.0.0", port=5000, debug=False)
