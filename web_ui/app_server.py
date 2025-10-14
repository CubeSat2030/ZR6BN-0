# =========================================================================
# Kabot-1 Mission Control Dashboard Server - THREAD-SAFE VERSION
# =========================================================================
# FIX: Added 'beacon' to SCRIPTS_CONFIG and updated api_start_pickup_beacon
# to call 'beacon' instead of 'main'.
# =========================================================================

import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
import shutil # <--- ADDED for data wipe
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
LOG_DIR = SRC_DIR / "logger" # Data folder location: src/logger/
PLOT_DIR = SRC_DIR / "plotter"
CHARTS_DIR = PLOT_DIR / "charts" # Charts folder location: src/plotter/charts/
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- Global State ---
RUNNING_PROCESSES = {}
PROCESSES_LOCK = threading.Lock()
AUTO_START_TIMEOUT = 30 # seconds
BUZZER_THREAD_STOP = threading.Event()

# --- Script Configuration ---
# NOTE: The 'main_controller' entry must always be present.
# 'log_script' is the file run for manual logger scripts.
# 'plot_script' is the file run to generate a chart.
# 'chart_file' is the resulting chart filename.
SCRIPTS_CONFIG = {
    "main_controller": {
        "title": "Main Flight Controller",
        "is_main_controller": True # Special flag
    },
    "gps": {
        "title": "GPS Logger",
        "log_script": SRC_DIR / "gps.py",
        "plot_script": PLOT_DIR / "gps_plotter.py",
        "chart_file": "gps_chart.svg"
    },
    "bme280": {
        "title": "BME280 Logger",
        "log_script": SRC_DIR / "bme280.py",
        "plot_script": PLOT_DIR / "bme280_plotter.py",
        "chart_file": "bme280_chart.svg"
    },
    "mpu6050": {
        "title": "MPU6050 Logger",
        "log_script": SRC_DIR / "mpu6050.py",
        "plot_script": PLOT_DIR / "mpu6050_plotter.py",
        "chart_file": "mpu_chart.svg"
    }
    ,
    "beacon": {
        "title": "Bluetooth PAN Hotspot",
        "log_script": SRC_DIR / "beacon.py",
        "is_main_controller": False # Ensure it can run concurrently with main
    }
}

# =========================================================================
# System & Script Control Functions (Thread-Safe)
# =========================================================================

def is_main_controller_active():
    """Checks if the main flight script is currently running."""
    with PROCESSES_LOCK:
        proc = RUNNING_PROCESSES.get('main_controller')
        return proc is not None and proc.poll() is None

def stop_script(name):
    """Stops a running subprocess by name."""
    with PROCESSES_LOCK:
        proc = RUNNING_PROCESSES.pop(name, None)
    
    if proc and proc.poll() is None:
        try:
            print(f"[CONTROL] Terminating {name} (PID: {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"[CONTROL] {name} did not terminate gracefully, killing.")
                proc.kill()
            return True, f"{SCRIPTS_CONFIG.get(name, {}).get('title', name)} stopped successfully."
        except Exception as e:
            print(f"[ERROR] Failed to stop {name}: {e}")
            return False, f"Error stopping {SCRIPTS_CONFIG.get(name, {}).get('title', name)}: {e}"
    elif proc:
        return True, f"{SCRIPTS_CONFIG.get(name, {}).get('title', name)} was already stopped."
    else:
        return False, f"{SCRIPTS_CONFIG.get(name, {}).get('title', name)} is not currently running."

def start_script(name):
    """Starts a script, checking for main controller conflicts."""
    config = SCRIPTS_CONFIG.get(name)

    if not config:
        return False, f"Unknown script name: {name}"

    with PROCESSES_LOCK:
        # 1. Check if the script is already running
        if name in RUNNING_PROCESSES and RUNNING_PROCESSES[name].poll() is None:
            return False, f"{config['title']} is already running (PID: {RUNNING_PROCESSES[name].pid})."
            
        # 2. Check for main controller conflict for manual scripts
        if not config.get('is_main_controller', False) and name != 'beacon':
            if is_main_controller_active():
                return False, f"Cannot start manual logger while Main Flight Controller is active."

    # Determine the file path
    if config.get('is_main_controller'):
        script_path = MAIN_CONTROLLER_SCRIPT
    else:
        script_path = config.get('log_script')

    if not script_path or not script_path.exists():
        return False, f"Script file not found: {script_path}"
        
    try:
        command = [sys.executable, str(script_path)]
        print(f"[CONTROL] Starting {name}: {' '.join(command)}")
        
        # Start the subprocess
        proc = subprocess.Popen(command, cwd=SRC_DIR)
        
        with PROCESSES_LOCK:
            RUNNING_PROCESSES[name] = proc
            
        return True, f"{config['title']} started successfully (PID: {proc.pid})."
    except Exception as e:
        print(f"[ERROR] Failed to start {name}: {e}")
        return False, f"Error starting {config['title']}: {e}"

# =========================================================================
# Utility & Buzzer Control
# =========================================================================

def start_buzzer_countdown():
    """Manages the startup countdown and ongoing heartbeat."""
    if not BUZZER_AVAILABLE:
        return

    # Startup alarm before auto-start (if enabled)
    time.sleep(AUTO_START_TIMEOUT - 3)
    if BUZZER_THREAD_STOP.is_set(): return
    
    # 3-second solid alarm before launch
    print("[BUZZER] Launch alarm...")
    for _ in range(3):
        BUZZER.on()
        time.sleep(0.5)
        BUZZER.off()
        time.sleep(0.5)

    # Ongoing heartbeat loop (2 quick beeps every 10 seconds)
    while not BUZZER_THREAD_STOP.is_set():
        BUZZER.on()
        time.sleep(0.1)
        BUZZER.off()
        time.sleep(0.1)
        BUZZER.on()
        time.sleep(0.1)
        BUZZER.off()

        # Wait for the main period (10 seconds - 3 beeps * 0.2s + 0.1s total)
        time.sleep(9.5)


# =========================================================================
# Flask Application Setup
# =========================================================================

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder='../static')

@app.route('/')
def dashboard():
    """Renders the main dashboard template."""
    return render_template('dashboard.html', scripts_config=SCRIPTS_CONFIG)

@app.route('/chart/<filename>')
def serve_chart(filename):
    """Serves the generated chart images."""
    return send_from_directory(CHARTS_DIR, filename)

@app.route('/api/status')
def api_status():
    """Returns the current status of all running scripts."""
    status = {}
    with PROCESSES_LOCK:
        # Check all configured scripts (including main)
        for name, config in SCRIPTS_CONFIG.items():
            proc = RUNNING_PROCESSES.get(name)
            is_running = proc is not None and proc.poll() is None
            status[name] = {
                "running": is_running,
                "pid": proc.pid if is_running else None
            }
        
        # Manually check for main controller if not explicitly managed
        if 'main_controller' not in status:
             status['main_controller'] = {"running": is_main_controller_active(), "pid": None}

    return jsonify(status)

# =========================================================================
# API Endpoints: Script Control (Start/Stop)
# =========================================================================

@app.route('/api/script/<string:name>/<string:action>', methods=['POST'])
def api_script_control(name, action):
    """API endpoint to start or stop a specific manual logger script."""
    if name == 'main_controller' or name == 'beacon':
        return jsonify({"success": False, "message": "Use dedicated control routes for Main Controller and Beacon."}), 400
        
    if action == 'start':
        success, message = start_script(name)
    elif action == 'stop':
        success, message = stop_script(name)
    else:
        return jsonify({"success": False, "message": "Invalid action command."}), 400
        
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 500

@app.route('/api/script/main_controller/<string:action>', methods=['POST'])
def api_main_controller_control(action):
    """API endpoint to start or stop the main flight controller."""
    if action == 'start':
        with PROCESSES_LOCK:
            # Stop all other manual loggers before starting main
            for name in list(RUNNING_PROCESSES.keys()):
                if name != 'main_controller':
                    stop_script(name)
        
        success, message = start_script('main_controller')
    elif action == 'stop':
        success, message = stop_script('main_controller')
    else:
        return jsonify({"success": False, "message": "Invalid action command for Main Controller."}), 400

    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 500

# =========================================================================
# API Endpoints: Chart Generation
# =========================================================================

@app.route('/api/chart/<string:name>', methods=['POST'])
def api_generate_chart(name):
    """API endpoint to generate a chart for a specific script."""
    if name == 'main_controller' or name == 'beacon' or name not in SCRIPTS_CONFIG:
        return jsonify({"success": False, "message": "Invalid script for chart generation."}), 400
    
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Chart generation disabled while Main Controller is active."}), 400

    config = SCRIPTS_CONFIG[name]
    plot_script_path = config.get('plot_script')
    
    if not plot_script_path or not plot_script_path.exists():
        return jsonify({"success": False, "message": f"Plotter script not found: {plot_script_path}"}), 500

    try:
        command = [sys.executable, str(plot_script_path)]
        print(f"[PLOT] Running chart generator for {name}: {' '.join(command)}")
        
        # Run the plotter script synchronously and capture output
        result = subprocess.run(command, capture_output=True, text=True, cwd=PLOT_DIR, timeout=20)
        
        if result.returncode == 0:
            return jsonify({"success": True, "message": f"Chart for {config['title']} generated successfully."}), 200
        else:
            error_message = f"Plotting script failed: {result.stderr.strip() or 'No error output.'}"
            print(f"[ERROR] {error_message}")
            return jsonify({"success": False, "message": error_message}), 500

    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "message": "Chart generation timed out."}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred during plotting: {e}"}), 500

# =========================================================================
# API Endpoints: System Control
# =========================================================================

@app.route('/api/control/shutdown', methods=['POST'])
def api_shutdown():
    """API endpoint to shut down the RPi."""
    print("[SYSTEM] Initiating system shutdown in 5 seconds.")
    # Stop all running scripts first
    for name in list(RUNNING_PROCESSES.keys()):
        stop_script(name)
        
    def execute_shutdown():
        time.sleep(5)
        subprocess.run(["sudo", "shutdown", "now"])
        
    threading.Thread(target=execute_shutdown).start()
    return jsonify({"success": True, "message": "Kabot-1 is shutting down. Connection will be lost."}), 200

@app.route('/api/control/reboot', methods=['POST'])
def api_reboot():
    """API endpoint to reboot the RPi."""
    print("[SYSTEM] Initiating system reboot in 5 seconds.")
    # Stop all running scripts first
    for name in list(RUNNING_PROCESSES.keys()):
        stop_script(name)
        
    def execute_reboot():
        time.sleep(5)
        subprocess.run(["sudo", "reboot"])
        
    threading.Thread(target=execute_reboot).start()
    return jsonify({"success": True, "message": "Kabot-1 is rebooting. Connection will be lost."}), 200

@app.route('/api/control/wipe_data', methods=['POST'])
def api_wipe_data():
    """API endpoint to wipe all logged data and generated charts."""
    # Ensure no scripts are running that might be writing to these directories
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Cannot wipe data while Main Controller is active."}), 400
    
    # Stop all other manual loggers just to be safe
    for name in list(RUNNING_PROCESSES.keys()):
        if name != 'main_controller':
            stop_script(name)
            
    print("[SYSTEM] Wiping log data and charts...")
    
    # 1. Wipe Log Data
    try:
        if LOG_DIR.exists():
            shutil.rmtree(LOG_DIR)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error wiping log data: {e}"}), 500

    # 2. Wipe Charts
    try:
        if CHARTS_DIR.exists():
            shutil.rmtree(CHARTS_DIR)
        CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error wiping chart data: {e}"}), 500
    
    print("[SYSTEM] Data wipe complete.")
    return jsonify({"success": True, "message": "All log files and generated charts have been permanently deleted."}), 200

@app.route('/api/control/start_pickup_beacon', methods=['POST'])
def api_start_pickup_beacon():
    """API endpoint to start the pickup beacon (beacon.py)."""
    # NOTE: We allow the beacon to run concurrently with the main controller if needed,
    # but the primary use case is during the recovery/pickup phase.
    if 'beacon' in RUNNING_PROCESSES and RUNNING_PROCESSES['beacon'].poll() is None:
         return jsonify({"success": False, "message": "Bluetooth Beacon is already running."}), 400
        
    success, message = start_script('beacon')
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 500

# =========================================================================        


if __name__ == "__main__":
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    def exit_handler(signum, frame):
        if BUZZER_AVAILABLE:
            BUZZER.off()
        BUZZER_THREAD_STOP.set()
        print("\n[CLEANUP] Buzzer and countdown thread stopped.")
        # Stop all processes on exit
        for name in list(RUNNING_PROCESSES.keys()):
            stop_script(name)
        sys.exit(0)
        
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    
    print("------------------------------------------------------------------")
    print("Kabot-1 Mission Control Dashboard is starting...")
    print(f"Access the dashboard at: http://0.0.0.0:5000/")
    print(f"Auto-Start Timeout: {AUTO_START_TIMEOUT} seconds.")
    if BUZZER_AVAILABLE:
        print("Buzzer Countdown: ACTIVE on GPIO 21.")
        print("Status: Standby Heartbeat (2 quick beeps/10s) while connected.")
        print("Alarm: Solid beep for 3 seconds before auto-start.") 
    else:
        print("Buzzer Countdown: INACTIVE (gpiozero not found or failed to initialize).")
    print("------------------------------------------------------------------")

    # The main controller script will be started automatically if it's past the timeout
    # This logic is currently managed by the buzzer countdown thread in real deployment.
    # We will rely on the user to manually launch the script for now until deployment logic is finalized.
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

