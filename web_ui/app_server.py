# =========================================================================
# Kabot-1 Mission Control Dashboard Server - THREAD-SAFE VERSION
# =========================================================================
# FIX: Added threading.Lock around all access to the global RUNNING_PROCESSES
# dictionary to prevent Internal Server Errors (500) due to race conditions.
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
SIM_DIR = SRC_DIR / "simulation"
CHARTS_DIR = PLOT_DIR / "charts" # Charts folder location: src/plotter/charts/
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Global State and Timer Configuration ---
AUTO_START_TIMEOUT = 60 # Seconds
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()

# --- Flask App Initialization ---
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock() # CRITICAL: Lock for thread safety

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
    "sound": {
        "title": "Payload Flight Simulation",
        "sim_script": SIM_DIR / "payload_flight_simulation.py",
        "video_file": "payload_flight_simulation.mp4"
    }
}

# =========================================================================
# SYSTEM PROCESS CHECK & CONTROL FUNCTIONS (THREAD-SAFE)
# =========================================================================

def is_main_controller_active():
    """Checks if main.py is currently running."""
    with PROCESS_LOCK:
        if 'main' in RUNNING_PROCESSES:
            if RUNNING_PROCESSES['main'].poll() is None:
                return True
            else:
                del RUNNING_PROCESSES['main'] 
        return False

def get_status():
    """Returns the current status of all scripts."""
    status = {}
    running_state = {}
    
    with PROCESS_LOCK:
        # Check and update the state of all running processes safely
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

    # Build the final status dictionary outside the lock
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
    script_path = str(config['log_script']) 
    
    with PROCESS_LOCK: # Acquire lock for process manipulation
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
    
    if name != 'main' and is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Manual loggers cannot be stopped."

    with PROCESS_LOCK: # Acquire lock for process manipulation
        if name not in RUNNING_PROCESSES or RUNNING_PROCESSES[name].poll() is not None:
            return False, f"{SCRIPTS_CONFIG.get(name, {}).get('title', name)} is not running or has already stopped."

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
            return False, f"Failed to stop {name}. Process entry cleared."

def run_plotter(name):
    """Runs a Python plotter script synchronously."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Chart generation is disabled."
        
    if name not in SCRIPTS_CONFIG or 'plot_script' not in SCRIPTS_CONFIG[name]:
        return False, "Unknown or non-plotter script name."
    
    # ... (Plotter logic remains unchanged as it doesn't touch RUNNING_PROCESSES)
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['plot_script']) 
    chart_file = config['chart_file']
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=3000, # Gives each plotter scripts a timeout of 5 minutes each to prevent any deadlocks. 
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

def wipe_data_and_charts():
    """Deletes all .txt files in LOG_DIR and the entire CHARTS_DIR."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Data wipe is disabled."

    log_success = True
    chart_success = True
    
    # 1. Delete all .txt files in the log directory (src/logger/)
    log_file_count = 0
    try:
        for file in LOG_DIR.glob("*.txt"):
            if file.is_file():
                os.remove(file)
                log_file_count += 1
        print(f"[DATA WIPE] Deleted {log_file_count} log files from {LOG_DIR}")
    except Exception as e:
        log_success = False
        print(f"[DATA WIPE ERROR] Failed to delete log files: {e}")

    # 2. Delete the entire charts directory (src/plotter/charts/) and recreate it
    chart_file_count = 0
    try:
        if CHARTS_DIR.exists():
            # Count files before deletion (approximate)
            chart_file_count = len(list(CHARTS_DIR.glob("*.svg")))
            shutil.rmtree(CHARTS_DIR)
            print(f"[DATA WIPE] Deleted {chart_file_count} charts and the directory {CHARTS_DIR}")
        
        # Always attempt to recreate the directory for future plotting
        CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        
    except Exception as e:
        chart_success = False
        print(f"[DATA WIPE ERROR] Failed to delete/recreate charts directory: {e}")
        
    if log_success and chart_success:
        return True, f"Successfully wiped {log_file_count} log files and {chart_file_count} chart files."
    else:
        msg = "Partial success/failure during wipe: "
        if not log_success: msg += "Failed to clean log files. "
        if not chart_success: msg += "Failed to clean charts folder. "
        return False, msg.strip()


# =========================================================================
# BUZZER COUNTDOWN AND AUTO-START LOGIC
# =========================================================================

def reset_auto_start_timer():
    """Stops the buzzer and resets the auto-start timer."""
    global LAST_CONNECTION_TIME
    if BUZZER_AVAILABLE:
        BUZZER.off() 
    
    if not is_main_controller_active():
        LAST_CONNECTION_TIME = time.time()

#  Start of double beep function...
#
#
# Commented the buzzer_double_beep function 
# because it unnessacery use of ram and it gets annoying  and impacts performance while using the web ui.
#
# def buzzer_double_beep(delay_between_beeps=0.1, total_duration=60.0): # 10.0s total pulse  pause interval
#   Executes the two rapid beeps and waits for the remaining duration.
#
#    if not BUZZER_AVAILABLE:
#        time.sleep(total_duration)
#        return
#        
#    start_wait = time.time()
#    
#    # Beep 1
#    BUZZER.on()
#    time.sleep(delay_between_beeps)
#    BUZZER.off()
#    
#    # Short pause
#    time.sleep(delay_between_beeps)
#    
#    # Beep 2
#    BUZZER.on()
#    time.sleep(delay_between_beeps)
#    BUZZER.off()
#    
#    # Wait for the remaining time
#    remaining_wait = total_duration - (time.time() - start_wait)
#    if remaining_wait >
#
#
# End of double beep function...

def start_buzzer_countdown():
#-------------TODO---------------
# Replace the use of delays to  simulate the rapid countdown affect with poll frequencies.
# The benafit of using polling frequencies is that it does not delay the entire program thus not causing any
#  conflicts and  thus optimizes the overall code and performance.
# The use of polling frequencies will also allow me to acheive much more fluide countdown sfx
    """
    Runs in a background thread. Manages the countdown, buzzer beeping, 
    and automatically launches main.py if the timer expires.
    """
    global LAST_CONNECTION_TIME
    global BUZZER_THREAD_STOP
    
    while not BUZZER_THREAD_STOP.is_set():
        
        if is_main_controller_active(): # if main.py is running the buzzer must remain silent.
            if BUZZER_AVAILABLE:
                BUZZER.off()
            time.sleep(5)
            continue
            
        time_elapsed = time.time() - LAST_CONNECTION_TIME
        time_remaining = AUTO_START_TIMEOUT - time_elapsed
        
        if time_remaining <= 0:
            # --- AUTO-START TRIGGERED: SOLID BEEP FOR 3 SECONDS ---
            print("\n[AUTO-START] Timeout reached. Launching Flight Controller...")
            
            if BUZZER_AVAILABLE:
               # BUZZER.on() # Solid beep ON
               # time.sleep(3.0) # Wait for 3 seconds
                BUZZER.off() # Solid beep OFF
            
            # The start_script call is now thread-safe
            success, message = start_script('main') 
            
            if success:
                print(f"[AUTO-START SUCCESS] {message}")
            else:
                print(f"[AUTO-START FAILURE] {message}")
            
            time.sleep(5) 
            
        elif time_remaining < AUTO_START_TIMEOUT - 5: 
            # --- COUNTDOWN BEEPING ---
            
            if time_remaining <= 5:
                # SUPER SUPER FAST BEEP
                delay = 0.0625
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(delay)
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(delay)
     
            
            if time_remaining <= 10:
                # SUPER FAST BEEP
                delay = 0.125
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(delay)
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(delay)
     
            
            if time_remaining <= 20:
                # FAST BEEP
                delay = 0.25
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(delay)
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(delay)
                
            elif time_remaining <= 30:
                # MEDIUM BEEP
                delay = 0.5
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(delay)
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(delay)

            else:
                # SLOW BEEP
                delay = 1.0 
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(0.1) 
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(delay - 0.1)
            
        else: 
            # --- CONNECTION STANDBY HEARTBEAT ---
            buzzer_double_beep(delay_between_beeps=0.1, total_duration=10.0)


@app.before_request
def update_last_connection_time():
    """Hook runs before every request to reset the auto-start timer."""
    reset_auto_start_timer()


# =========================================================================
# FLASK API ROUTES (UNCHANGED)
# =========================================================================

@app.route("/")
def index():
    serializable_config = {}
    for key, config in SCRIPTS_CONFIG.items():
        if not config.get('is_main_controller'):
            serializable_config[key] = {
                "title": config["title"],
                "chart_file": config["chart_file"] 
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
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller is active. Cannot generate charts."}), 403
        
    success, message = run_plotter(name)
    return jsonify({"success": success, "message": message})

@app.route("/chart/<path:filename>")
def get_chart_display(filename):
    if ".." in filename or "/" in filename: abort(400)
    return send_from_directory(CHARTS_DIR, filename, as_attachment=False)

@app.route("/download/chart/<filename>")
def download_chart(filename):
    if ".." in filename or "/" in filename: abort(400)
    file_path = CHARTS_DIR / filename
    if not file_path.exists(): abort(404, description="Chart not found.")
    return send_from_directory(CHARTS_DIR, filename, as_attachment=True)
    
@app.route('/api/control/<action>', methods=['POST'])
def api_system_control(action):
    if action == 'reboot':
        cmd = ["sudo", "reboot"]
        message = "Kabot-1 will reboot momentarily."
    elif action == 'shutdown':
        cmd = ["sudo", "shutdown", "now"]
        message = "Kabot-1 will shut down momentarily."
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

@app.route('/api/control/wipe_data', methods=['POST'])
def api_wipe_data(): # <--- NEW ROUTE for data wipe
    """API endpoint to wipe all logged data and generated charts."""
    success, message = wipe_data_and_charts()
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        # Use 403 Forbidden if the main controller is running
        if "Flight Controller" in message:
            return jsonify({"success": False, "message": message}), 403
        else:
            return jsonify({"success": False, "message": message}), 500


if __name__ == "__main__":
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    def exit_handler(signum, frame):
        if BUZZER_AVAILABLE:
            BUZZER.off()
        BUZZER_THREAD_STOP.set()
        print("\n[CLEANUP] Buzzer and countdown thread stopped.")
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
    app.run(host="0.0.0.0", port=5000, debug=False)
