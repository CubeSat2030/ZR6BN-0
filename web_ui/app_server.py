# =========================================================================
# Kabot-1 Mission Control Dashboard Server - COMPLETE THREAD-SAFE VERSION
# =========================================================================
# Updated: January 2026 - Full video support + complete buzzer logic
# - Fixed: All buzzer/countdown functions included
# - Video serving from src/plotter/videos with proper MIME type
# - Thread-safe process management
# =========================================================================

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
    print("[WARNING] gpiozero or RPi.GPIO not available. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False
    BUZZER = None
except Exception as e:
    print(f"[WARNING] Could not initialize Buzzer on GPIO 21: {e}. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False
    BUZZER = None

# --- Configuration ---
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MAIN_CONTROLLER_SCRIPT = BASE_DIR / "main.py"
SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger"
PLOT_DIR = SRC_DIR / "plotter"
SIM_DIR = SRC_DIR / "simulation" / "scripts"
CHARTS_DIR = PLOT_DIR / "charts"
VIDEOS_DIR = PLOT_DIR / "videos"  # ← VIDEO EXPORT DIRECTORY (create if missing)
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

# Ensure directories exist
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Data wipe paths
DATA_DIR = LOG_DIR / "data" / "1_preflight"
HEARTBEATS_DIR = LOG_DIR / "heartbeats"
FOOTAGE_DIR = SRC_DIR / "photography" / "footage"

# --- Global State ---
AUTO_START_TIMEOUT = 60  # Seconds
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()
LAST_BEEP_TIME = 0
SOLID_BEEP_START_TIME = None

# --- Flask App ---
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()

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
        "video_file": "BACAR13_stable_replay.mp4",  # ← Just filename!
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
    """Check if main.py is currently running."""
    with PROCESS_LOCK:
        if 'main' in RUNNING_PROCESSES:
            if RUNNING_PROCESSES['main'].poll() is None:
                return True
            else:
                del RUNNING_PROCESSES['main']
        return False

def get_status():
    """Returns current status of all scripts."""
    status = {}
    running_state = {}
    
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
            running_state[name] = {'running': is_running, 'pid': pid}
    
    for name, config in SCRIPTS_CONFIG.items():
        state = running_state[name]
        if config.get('is_main_controller', False):
            status['main_controller'] = {
                "running": state['running'],
                "title": config['title'],
                "pid": state['pid'],
            }
        else:
            status[name] = {
                "title": config['title'],
                "running": state['running'],
                "pid": state['pid'],
                "chart_file": config.get('chart_file')
            }
    
    if 'main_controller' not in status:
        status['main_controller'] = {
            "running": False,
            "title": SCRIPTS_CONFIG['main']['title'],
            "pid": None,
        }
    
    return status

def start_script(name):
    """Starts a Python script in a non-blocking subprocess."""
    if name != 'main' and is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Manual loggers are disabled."
    
    if name not in SCRIPTS_CONFIG:
        return False, "Unknown script name."
    
    config = SCRIPTS_CONFIG[name]
    script_path_key = 'log_script' if 'log_script' in config else ('sim_script' if 'sim_script' in config else None)
    
    if not script_path_key:
        return False, f"Configuration for '{name}' is missing a script path."
    script_path = str(config[script_path_key])
    
    with PROCESS_LOCK:
        if name in RUNNING_PROCESSES and RUNNING_PROCESSES[name].poll() is None:
            return False, f"{config['title']} is already running (PID: {RUNNING_PROCESSES[name].pid})."
        
        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(BASE_DIR)
            )
            RUNNING_PROCESSES[name] = process
            
            if name == 'main':
                return True, f"Started Flight Controller (PID: {process.pid}). Loggers are now active."
            else:
                return True, f"Started {config['title']} (PID: {process.pid})."
        except Exception as e:
            return False, f"Failed to start {config['title']}: {str(e)}"

def stop_script(name):
    """Stops a running script by sending SIGTERM."""
    if name != 'main' and is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Manual loggers cannot be stopped."
    
    with PROCESS_LOCK:
        if name not in RUNNING_PROCESSES or RUNNING_PROCESSES[name].poll() is not None:
            return False, f"{SCRIPTS_CONFIG.get(name, {}).get('title', name)} is not running."
        
        try:
            os.killpg(os.getpgid(RUNNING_PROCESSES[name].pid), signal.SIGTERM)
            time.sleep(0.5)
            
            if name in RUNNING_PROCESSES:
                del RUNNING_PROCESSES[name]
                
            if name == 'main':
                return True, f"Stopped Flight Controller."
            else:
                return True, f"Stopped {SCRIPTS_CONFIG.get(name, {}).get('title', name)}."
        except Exception:
            if name in RUNNING_PROCESSES:
                del RUNNING_PROCESSES[name]
            return False, f"Failed to stop {name}."

def run_plotter(name):
    """Runs a Python plotter script synchronously."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Chart generation is disabled."
    
    if name not in SCRIPTS_CONFIG or 'plot_script' not in SCRIPTS_CONFIG[name]:
        return False, "Unknown or non-plotter script name."
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['plot_script'])
    chart_file = config['chart_file']
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=False,
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0 and (CHARTS_DIR / chart_file).exists():
            return True, f"Chart generated successfully: {chart_file}"
        else:
            error_msg = result.stderr.strip() or f"Plotter failed with exit code {result.returncode}."
            return False, f"Plotting failed: {error_msg}"
    except subprocess.TimeoutExpired:
        return False, f"Plotter {name} timed out after 120 seconds."
    except Exception as e:
        return False, f"Failed to run plotter {name}: {str(e)}"

def run_simulation(name):
    """Runs the simulation script synchronously to generate video."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Simulation is disabled."
    
    if name not in SCRIPTS_CONFIG or 'sim_script' not in SCRIPTS_CONFIG[name]:
        return False, "Unknown or non-simulation script name."
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['sim_script'])
    video_filename = config['video_file']
    video_path = VIDEOS_DIR / video_filename
    
    print(f"[SIMULATION] Starting video generation → {video_path}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=28800,  # 8 hours
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0 and video_path.exists():
            size_mb = video_path.stat().st_size / (1024 * 1024)
            print(f"[SIMULATION SUCCESS] {video_filename} created ({size_mb:.1f} MB)")
            return True, f"Simulation video generated: {video_filename}"
        else:
            error_msg = result.stderr.strip() or f"Exit code {result.returncode}"
            print(f"[SIMULATION ERROR] {error_msg}")
            return False, f"Simulation failed: {error_msg}"
    except subprocess.TimeoutExpired:
        return False, "Simulation timed out after 8 hours."
    except Exception as e:
        print(f"[SIMULATION EXCEPTION] {str(e)}")
        return False, f"Failed to run simulation: {str(e)}"

def wipe_data_and_charts():
    """Deletes all log data, charts, videos, heartbeats, and footage."""
    if is_main_controller_active():
        return False, "Flight Controller is running. Data wipe disabled."
    
    success = True
    total_deleted = 0
    
    # Files to delete
    patterns = [
        (LOG_DIR.glob("*.txt"), "logger txt files"),
        (DATA_DIR.glob("*"), "preflight data"),
        (HEARTBEATS_DIR.glob("*.json"), "heartbeats"),
        (CHARTS_DIR.glob("*"), "charts"),
        (VIDEOS_DIR.glob("*"), "videos"),
        (FOOTAGE_DIR.rglob("*"), "footage")
    ]
    
    for pattern, desc in patterns:
        try:
            count = sum(1 for item in pattern if item.is_file())
            for item in pattern:
                if item.is_file():
                    item.unlink()
            total_deleted += count
            if count > 0:
                print(f"[WIPE] Deleted {count} {desc}")
        except Exception as e:
            success = False
            print(f"[WIPE ERROR] {desc}: {e}")
    
    # Recreate empty directories
    for dir_path in [CHARTS_DIR, VIDEOS_DIR, DATA_DIR, HEARTBEATS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    if success:
        return True, f"Wiped {total_deleted} files successfully."
    return False, "Wipe completed with some errors - check logs."

# =========================================================================
# BUZZER COUNTDOWN & AUTO-START (COMPLETE IMPLEMENTATION)
# =========================================================================

def reset_auto_start_timer():
    """Reset timer on web connection."""
    global LAST_CONNECTION_TIME, SOLID_BEEP_START_TIME
    if BUZZER_AVAILABLE and BUZZER:
        BUZZER.off()
        SOLID_BEEP_START_TIME = None
    if not is_main_controller_active():
        LAST_CONNECTION_TIME = time.time()

def double_beep_and_wait(total_duration=10.0, beep_delay=0.1):
    """Non-blocking double beep for standby mode."""
    global LAST_BEEP_TIME
    
    if not BUZZER_AVAILABLE or not BUZZER:
        LAST_BEEP_TIME = time.time()
        return
    
    if time.time() - LAST_BEEP_TIME >= total_duration:
        start_time = time.time()
        
        # Beep 1
        BUZZER.on()
        time.sleep(beep_delay)
        BUZZER.off()
        
        # Pause
        time.sleep(beep_delay)
        
        # Beep 2
        BUZZER.on()
        time.sleep(beep_delay)
        BUZZER.off()
        
        LAST_BEEP_TIME = start_time

def start_buzzer_countdown():
    """Main buzzer countdown thread - handles all beeping logic."""
    global LAST_CONNECTION_TIME, LAST_BEEP_TIME, SOLID_BEEP_START_TIME
    
    LOOP_SLEEP = 0.1
    
    while not BUZZER_THREAD_STOP.is_set():
        current_time = time.time()
        
        # If main controller active, silence buzzer
        if is_main_controller_active():
            if BUZZER_AVAILABLE and BUZZER:
                BUZZER.off()
            SOLID_BEEP_START_TIME = None
            LAST_BEEP_TIME = current_time
            time.sleep(5)
            continue
        
        time_elapsed = current_time - LAST_CONNECTION_TIME
        time_remaining = AUTO_START_TIMEOUT - time_elapsed
        
        # AUTO-START: Timeout reached
        if time_remaining <= 0:
            if SOLID_BEEP_START_TIME is None:
                print("\n[AUTO-START] 60s timeout! Launching Flight Controller...")
                success, msg = start_script('main')
                print(f"[AUTO-START] {msg}")
                
                if BUZZER_AVAILABLE and BUZZER:
                    BUZZER.on()
                    SOLID_BEEP_START_TIME = current_time
            
            # Solid beep for 3 seconds
            if SOLID_BEEP_START_TIME and current_time - SOLID_BEEP_START_TIME >= 3.0:
                if BUZZER_AVAILABLE and BUZZER:
                    BUZZER.off()
                SOLID_BEEP_START_TIME = None
            
            time.sleep(LOOP_SLEEP)
            continue
        
        # COUNTDOWN BEEPING
        cycle_period = 0.0
        beep_duration = 0.0
        
        if time_remaining <= 5:
            cycle_period, beep_duration = 0.125, 0.0625  # Super fast
        elif time_remaining <= 10:
            cycle_period, beep_duration = 0.25, 0.125    # Fast
        elif time_remaining <= 20:
            cycle_period, beep_duration = 0.5, 0.25      # Medium
        elif time_remaining <= 30:
            cycle_period, beep_duration = 1.0, 0.5       # Slow
        elif time_remaining < AUTO_START_TIMEOUT - 5:
            cycle_period, beep_duration = 1.0, 0.1       # Very slow
        else:
            # Standby: double beep every 10s
            double_beep_and_wait(10.0, 0.1)
            time.sleep(LOOP_SLEEP)
            continue
        
        # Execute countdown beep cycle
        if cycle_period > 0 and BUZZER_AVAILABLE and BUZZER:
            time_since_beep = current_time - LAST_BEEP_TIME
            
            if time_since_beep < beep_duration:
                BUZZER.on()
            elif time_since_beep < cycle_period:
                BUZZER.off()
            else:
                LAST_BEEP_TIME = current_time
                BUZZER.on()
        
        time.sleep(LOOP_SLEEP)

# =========================================================================
# FLASK ROUTES
# =========================================================================

@app.route("/")
def index():
    serializable_config = {}
    for key, config in SCRIPTS_CONFIG.items():
        if not config.get('is_main_controller'):
            chart_file = config.get("chart_file")
            serializable_config[key] = {
                "title": config["title"],
                "chart_file": chart_file
            }
    return render_template("dashboard.html", scripts_config=serializable_config)

@app.route("/api/status", methods=['GET'])
def api_status():
    return jsonify(get_status())

@app.route('/api/script/<name>/<action>', methods=['POST'])
def api_script_control(name, action):
    if name == 'main_controller':
        name = 'main'
    
    if name != 'main' and is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller active. Manual control disabled."}), 403
    
    if action == 'start':
        success, message = start_script(name)
    elif action == 'stop':
        success, message = stop_script(name)
    else:
        return jsonify({"success": False, "message": "Invalid action."}), 400
    
    return jsonify({"success": success, "message": message, "status": get_status()})

@app.route('/api/chart/<name>', methods=['POST'])
def api_chart_generate(name):
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller active. Chart generation disabled."}), 403
    
    success, message = run_plotter(name)
    return jsonify({"success": success, "message": message})

@app.route('/api/simulation/<name>', methods=['POST'])
def api_simulation_generate(name):
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller active. Simulation disabled."}), 403
    
    success, message = run_simulation(name)
    return jsonify({"success": success, "message": message})

@app.route("/chart/<path:filename>")
def get_chart_display(filename):
    if ".." in filename or "/" in filename:
        abort(400)
    return send_from_directory(CHARTS_DIR, filename, as_attachment=False)

@app.route("/video/<path:filename>")
def get_video_display(filename):
    """Serve simulation video with proper MIME type - VIDEO FIX #1"""
    if ".." in filename or "/" in filename:
        abort(400, "Invalid filename")
    
    video_path = VIDEOS_DIR / filename
    
    if not video_path.exists():
        print(f"[VIDEO 404] {video_path} not found")
        abort(404, "Video not generated yet")
    
    print(f"[VIDEO SERVE] Serving {video_path} ({video_path.stat().st_size/1024/1024:.1f}MB)")
    return send_from_directory(
        VIDEOS_DIR,
        filename,
        mimetype='video/mp4',
        conditional=True
    )

@app.route("/download/chart/<filename>")
def download_chart(filename):
    if ".." in filename or "/" in filename:
        abort(400)
    file_path = CHARTS_DIR / filename
    if not file_path.exists():
        abort(404)
    return send_from_directory(CHARTS_DIR, filename, as_attachment=True)

@app.route('/api/control/<action>', methods=['POST'])
def api_system_control(action):
    if action == 'shutdown':
        cmd = ["sudo", "shutdown", "now"]
        message = "Kabot-1 shutting down..."
    elif action == 'reboot':
        cmd = ["sudo", "reboot"]
        message = "Kabot-1 rebooting..."
    elif action == 'wipe_data':
        success, message = wipe_data_and_charts()
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "message": message}), 403
    else:
        return jsonify({"success": False, "message": "Invalid action."}), 400
    
    try:
        subprocess.Popen(cmd, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return jsonify({"success": True, "message": message})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed: {str(e)}"}), 500

@app.before_request
def update_last_connection_time():
    reset_auto_start_timer()

# =========================================================================
# MAIN STARTUP
# =========================================================================

if __name__ == "__main__":
    # Start buzzer countdown thread
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    def exit_handler(signum, frame):
        print("\n[SHUTDOWN] Cleaning up...")
        if BUZZER_AVAILABLE and BUZZER:
            BUZZER.off()
        BUZZER_THREAD_STOP.set()
        time.sleep(0.5)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    
    print("=" * 60)
    print("KABOT-1 MISSION CONTROL DASHBOARD v2.0")
    print(f"Video directory: {VIDEOS_DIR}")
    print(f"Charts directory: {CHARTS_DIR}")
    print(f"Access: http://0.0.0.0:5000/")
    print(f"Auto-start: {AUTO_START_TIMEOUT}s timeout")
    if BUZZER_AVAILABLE:
        print("✅ Buzzer: ACTIVE (GPIO 21)")
    else:
        print("⚠️  Buzzer: DISABLED")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
