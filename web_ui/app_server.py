# =========================================================================
# Kabot-1 Mission Control Dashboard Server (OctoPrint Style) - FINAL & PATCHED
# =========================================================================
# Logic: app_server.py now treats main.py as a special, controllable script.
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

# Configuration map for all controllable scripts (main and loggers)
SCRIPTS_CONFIG = {
    # 1. ADD MAIN CONTROLLER as a controllable script
    "main": {
        "title": "Flight Controller (main.py)",
        "log_script": MAIN_CONTROLLER_SCRIPT, 
        "is_main_controller": True # Flag it as the critical script
    },
    # 2. Loggers (Workers)
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
# SYSTEM PROCESS CHECK & CONTROL FUNCTIONS
# =========================================================================

def is_main_controller_active():
    """Checks if main.py is currently running."""
    if 'main' in RUNNING_PROCESSES:
        if RUNNING_PROCESSES['main'].poll() is None:
            return True
        else:
            # Process died, remove it from tracking
            del RUNNING_PROCESSES['main'] 
    return False

def get_status():
    """Returns the current status of all scripts."""
    status = {}
    
    for name, config in SCRIPTS_CONFIG.items():
        is_running = False
        pid = None
        
        if name in RUNNING_PROCESSES:
            if RUNNING_PROCESSES[name].poll() is None:
                is_running = True
                pid = RUNNING_PROCESSES[name].pid
            else:
                del RUNNING_PROCESSES[name] 

        # Separate main controller status for easier frontend parsing
        if config.get('is_main_controller', False):
             status['main_controller'] = {
                "running": is_running,
                "title": config['title'],
                "pid": pid,
            }
        else:
            status[name] = {
                "title": config['title'],
                "running": is_running,
                "pid": pid,
                "chart_file": config.get('chart_file')
            }
            
    # Ensure 'main_controller' status always exists
    if 'main_controller' not in status:
         status['main_controller'] = {
            "running": False,
            "title": SCRIPTS_CONFIG['main']['title'],
            "pid": None,
        }
            
    return status

def start_script(name):
    """Starts a Python script in a non-blocking subprocess."""
    
    # 1. SPECIAL CASE: If main is running, prevent other loggers from starting
    if name != 'main' and is_main_controller_active():
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
        
        if name == 'main':
             return True, f"Started Flight Controller (PID: {process.pid}). Loggers are now active."
        else:
             return True, f"Started {config['title']} (PID: {process.pid})."
    except Exception as e:
        return False, f"Failed to start {config['title']}: {str(e)}"

def stop_script(name):
    """Stops a running script by sending a termination signal."""
    
    # 1. SPECIAL CASE: Prevent stopping loggers if the main controller is running
    if name != 'main' and is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Manual loggers cannot be stopped."

    if name not in RUNNING_PROCESSES or RUNNING_PROCESSES[name].poll() is not None:
        return False, f"{SCRIPTS_CONFIG.get(name, {}).get('title', name)} is not running or has already stopped."

    try:
        # Use os.killpg for reliable termination of the entire process group
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
        return False, f"Failed to stop {name}. Process entry cleared."

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
        # Only expose loggers and plotters to the main script_config view
        if not config.get('is_main_controller'):
            serializable_config[key] = {
                "title": config["title"],
                "chart_file": config["chart_file"] 
            }
        
    return render_template("dashboard.html", scripts_config=serializable_config)

@app.route("/api/status", methods=['GET'])
def api_status():
    """API endpoint to get the status of all scripts."""
    return jsonify(get_status())

@app.route('/api/script/<name>/<action>', methods=['POST'])
def api_script_control(name, action):
    """API endpoint to start or stop ANY script (main, dht, mpu, sound)."""
    
    # The frontend uses 'main_controller', so remap it back to 'main'
    if name == 'main_controller':
        name = 'main'
        
    # Prevent start/stop of manual loggers/plotters if main is active (handled in start/stop functions but reiterated here)
    if name != 'main' and is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller is active. Cannot control manual scripts."}), 403

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
    """API endpoint to execute OS commands (Reboot/Shutdown)."""
    if action == 'reboot':
        cmd = ["sudo", "reboot"]
        message = "System will reboot momentarily."
    elif action == 'shutdown':
        cmd = ["sudo", "shutdown", "now"]
        message = "System will shut down momentarily."
    else:
        return jsonify({"success": False, "message": "Invalid control action."}), 400

    try:
        # Popen is used to execute the command without waiting, allowing Flask to return a response
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
