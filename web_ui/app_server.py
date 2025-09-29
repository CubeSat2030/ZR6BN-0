# =========================================================================
# Kabot-1 Mission Control Dashboard Server (OctoPrint Style) - FINAL & PATCHED
# =========================================================================

import subprocess
import pathlib
import sys
import time
import signal
import os
from flask import Flask, render_template, jsonify, send_from_directory, abort

# --- Configuration ---
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MAIN_CONTROLLER_SCRIPT = BASE_DIR / "main.py"

SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger"
PLOT_DIR = SRC_DIR / "plotter"
CHARTS_DIR = PLOT_DIR / "charts"
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Flask App Initialization ---
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

RUNNING_PROCESSES = {}

SCRIPTS_CONFIG = {
    "dht": {
        "title": "DHT Sensor Logger",
        "log_script": LOG_DIR / "dht_logger.py",
        "plot_script": PLOT_DIR / "dht_plotter.py",
        "chart_file": "dht_chart.svg"
    },
    "mpu": {
        "title": "MPU-6050 Logger",
        "log_script": LOG_DIR / "mpu6050_logger.py",
        "plot_script": PLOT_DIR / "mpu6050_plotter.py",
        "chart_file": "mpu_chart.svg"
    },
    "sound": {
        "title": "Sound Logger",
        "log_script": LOG_DIR / "sound_logger.py",
        "plot_script": PLOT_DIR / "sound_plotter.py",
        "chart_file": "sound_chart.svg"
    }
}

# =========================================================================
# SYSTEM PROCESS CHECK & MAIN CONTROLLER PLACEHOLDERS
# =========================================================================

def is_main_controller_active():
    """Checks if main.py is currently running."""
    try:
        script_path_str = str(MAIN_CONTROLLER_SCRIPT)
        cmd = f"ps aux | grep '{sys.executable}' | grep '{script_path_str}' | grep -v 'grep' | grep -v '{pathlib.Path(__file__).name}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except Exception:
        return False

def start_main_controller_process():
    """Placeholder: Main controller must be launched externally."""
    return False, "Flight Controller must be started manually in the terminal using 'python3 main.py'."

def stop_main_controller_process():
    """Placeholder: Main controller must be terminated externally."""
    return False, "Flight Controller must be stopped via Ctrl+C in the terminal."

# =========================================================================
# SCRIPT CONTROL FUNCTIONS (get_status, start_script, stop_script, run_plotter)
# (functions omitted for brevity; they are identical to the previous complete script)
# =========================================================================
# NOTE: The functions 'get_status', 'start_script', 'stop_script', and 'run_plotter'
# from the previous response are fully functional and remain unchanged here.
# =========================================================================
def get_status():
    """Returns the current status of all loggers and the main controller."""
    status = {}
    main_active = is_main_controller_active()
    
    for name, config in SCRIPTS_CONFIG.items():
        is_running = False
        pid = None
        
        if name in RUNNING_PROCESSES:
            # Check if the process is still alive
            if RUNNING_PROCESSES[name].poll() is None:
                is_running = True
                pid = RUNNING_PROCESSES[name].pid
            else:
                # Process died, remove it from tracking
                del RUNNING_PROCESSES[name] 

        status[name] = {
            "title": config['title'],
            "running": is_running,
            "pid": pid,
            "chart_file": config['chart_file']
        }
        
    status['main_controller'] = {
        "running": main_active,
        "title": "Flight Controller (main.py)"
    }
    return status

def start_script(name):
    """Starts a Python logger script in a non-blocking subprocess."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Manual loggers are disabled."
        
    if name not in SCRIPTS_CONFIG:
        return False, "Unknown script name." 
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['log_script']) 
    
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
        return True, f"Started {config['title']} (PID: {process.pid})."
    except Exception as e:
        return False, f"Failed to start {config['title']}: {str(e)}"

def stop_script(name):
    """Stops a running script by sending a termination signal."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Manual loggers are disabled."
        
    if name not in RUNNING_PROCESSES or RUNNING_PROCESSES[name].poll() is not None:
        return False, f"{name} is not running or has already stopped."

    try:
        # Use os.killpg for reliable termination of the entire process group
        os.killpg(os.getpgid(RUNNING_PROCESSES[name].pid), signal.SIGTERM)
        time.sleep(0.5)
        
        # Clean up the process dictionary
        if name in RUNNING_PROCESSES:
            del RUNNING_PROCESSES[name]
            
        return True, f"Stopped {SCRIPTS_CONFIG.get(name, {}).get('title', name)}."
    except Exception:
        if name in RUNNING_PROCESSES:
            del RUNNING_PROCESSES[name]
        return False, f"Failed to stop {name}. Process entry cleared."

def run_plotter(name):
    """Runs a Python plotter script synchronously."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Chart generation is disabled."
        
    if name not in SCRIPTS_CONFIG:
        return False, "Unknown plotter name."
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['plot_script']) 
    chart_file = config['chart_file']
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=45, 
            cwd=str(BASE_DIR) 
        )
        
        if result.returncode == 0 and os.path.exists(CHARTS_DIR / chart_file):
            return True, f"Chart generated successfully: {chart_file}"
        else:
            error_msg = result.stderr.strip() or f"Plotter failed with exit code {result.returncode}."
            return False, f"Plotting failed: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, f"Plotter {name} timed out after 45 seconds."
    except Exception as e:
        return False, f"Failed to run plotter {name}: {str(e)}"
# =========================================================================
# FLASK API ROUTES
# =========================================================================

@app.route("/")
def index():
    """Serves the main dashboard page."""
    serializable_config = {}
    for key, config in SCRIPTS_CONFIG.items():
        serializable_config[key] = {
            "title": config["title"],
            "chart_file": config["chart_file"] 
        }
        
    return render_template("dashboard.html", scripts_config=serializable_config)

@app.route("/api/status", methods=['GET'])
def api_status():
    """API endpoint to get the status of all loggers and the main controller."""
    return jsonify(get_status())

@app.route('/api/flight_controller/<action>', methods=['POST'])
def api_flight_controller(action):
    """
    NEW: Handles Start/Stop Flight button clicks and prevents the 'Unknown script name' error.
    Returns 405 to reinforce terminal control.
    """
    if action == 'start':
        success, message = start_main_controller_process()
    elif action == 'stop':
        success, message = stop_main_controller_process()
    else:
        return jsonify({"success": False, "message": "Invalid flight controller action."}), 400

    # Frontend fix is needed to hit this route, then it returns this message:
    return jsonify({"success": success, "message": message}), 405

@app.route('/api/script/<name>/<action>', methods=['POST'])
def api_script_control(name, action):
    """API endpoint to start or stop a logger script (dht, mpu, sound)."""
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller is active. Cannot control loggers."}), 403

    if action == 'start':
        success, message = start_script(name)
    elif action == 'stop':
        success, message = stop_script(name)
    else:
        return jsonify({"success": False, "message": "Invalid action."}), 400
    
    return jsonify({"success": success, "message": message, "status": get_status()})

@app.route('/api/chart/<name>', methods=['POST'])
def api_chart_generate(name):
    """API endpoint to run a plotter script."""
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller is active. Cannot generate charts."}), 403
        
    success, message = run_plotter(name)
    return jsonify({"success": success, "message": message})

@app.route("/chart/<path:filename>")
def get_chart_display(filename):
    """Serves a specific chart image for display in the browser."""
    if ".." in filename or "/" in filename:
        abort(400)
        
    return send_from_directory(CHARTS_DIR, filename, as_attachment=False)

@app.route("/download/chart/<filename>")
def download_chart(filename):
    """Serves a specific chart image for download (as attachment)."""
    if ".." in filename or "/" in filename:
        abort(400)
        
    file_path = CHARTS_DIR / filename
    if not file_path.exists():
        abort(404, description="Chart not found.")
        
    return send_from_directory(CHARTS_DIR, filename, as_attachment=True)
    
@app.route('/api/control/<action>', methods=['POST'])
def api_system_control(action):
    """RESTORED: API endpoint to execute OS commands (Reboot/Shutdown)."""
    if action == 'reboot':
        cmd = ["sudo", "reboot"]
        message = "System will reboot momentarily."
    elif action == 'shutdown':
        cmd = ["sudo", "shutdown", "now"]
        message = "System will shut down momentarily."
    else:
        return jsonify({"success": False, "message": "Invalid control action."}), 400

    try:
        subprocess.Popen(
            cmd, 
            start_new_session=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return jsonify({"success": True, "message": message})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to execute command: {str(e)}"}), 500


if __name__ == "__main__":
    print("------------------------------------------------------------------")
    print("Kabot-1 Mission Control Dashboard is starting...")
    print(f"Access the dashboard at: http://0.0.0.0:5000/")
    print("------------------------------------------------------------------")
    app.run(host="0.0.0.0", port=5000, debug=True)
