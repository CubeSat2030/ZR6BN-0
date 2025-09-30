# =========================================================================
# Kabot-1 Mission Control Dashboard Server - THREAD-SAFE VERSION
# =========================================================================
# FIX: Added threading.Lock around all access to the global RUNNING_PROCESSES
# dictionary to prevent Internal Server Errors (500) due to race conditions.
# UPDATE 1: Increased PLOTTER_TIMEOUT to 300s.
# FIX 5: Reworked the countdown to use the fluid, accelerating frequency 
#        starting from the full 60-second AUTO_START_TIMEOUT down to 0s. 
#        (Minimum frequency is 0.2Hz (1 beep/5s) at 60s.)
# FIX 6: Removed "Haywire" feature. Timer reset now results in an immediate,
#        clean reset of the buzzer (BUZZER.off()) and the timer.
# =========================================================================

import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
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
CHARTS_DIR = PLOT_DIR / "charts"
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Global State and Timer Configuration ---
AUTO_START_TIMEOUT = 60 # Seconds
PLOTTER_TIMEOUT = 300   # Seconds (5 minutes)
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()
# BUZZER_HAYWIRE_EVENT is removed for clean operation.

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
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['plot_script']) 
    chart_file = config['chart_file']
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=PLOTTER_TIMEOUT, 
            cwd=str(BASE_DIR) 
        )
        
        if result.returncode == 0 and os.path.exists(CHARTS_DIR / chart_file):
            return True, f"Chart generated successfully: {chart_file}"
        else:
            error_msg = result.stderr.strip() or f"Plotter failed with exit code {result.returncode}."
            return False, f"Plotting failed: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, f"Plotter {name} timed out after {PLOTTER_TIMEOUT} seconds." 
    except Exception as e:
        return False, f"Failed to run plotter {name}: {str(e)}"


# =========================================================================
# BUZZER COUNTDOWN AND AUTO-START LOGIC
# =========================================================================

def start_buzzer_countdown():
    """
    Runs in a background thread. Manages the countdown, buzzer beeping, 
    and automatically launches main.py if the timer expires.
    """
    global LAST_CONNECTION_TIME
    global BUZZER_THREAD_STOP

    # --- Fluid Beeping Constants and State ---
    COUNTDOWN_START = AUTO_START_TIMEOUT # 60.0 seconds
    MAX_FREQ = 8.0         # Max beeps/second (at 0s remaining)
    MIN_FREQ = 0.20        # Min beeps/second (at 60s remaining) -> 1 beep every 5 seconds
    CYCLE_TIME = 0.05      # Fixed thread loop cycle time (20 Hz update)
    current_time_in_cycle = 0.0 # Tracks time within the current beep/pause cycle
    
    while not BUZZER_THREAD_STOP.is_set():
        
        if is_main_controller_active():
            if BUZZER_AVAILABLE:
                BUZZER.off()
            time.sleep(5)
            # Reset fluid state when main is active or stopped
            current_time_in_cycle = 0.0 
            continue
            
        # The haywire logic has been removed. The timer reset is now handled 
        # instantly by the @app.before_request hook.
        
        time_elapsed = time.time() - LAST_CONNECTION_TIME
        time_remaining = AUTO_START_TIMEOUT - time_elapsed
        
        if time_remaining <= 0:
            # --- AUTO-START TRIGGERED: SOLID BEEP FOR 3 SECONDS ---
            print("\n[AUTO-START] Timeout reached. Launching Flight Controller...")
            
            if BUZZER_AVAILABLE:
               # BUZZER.on() # Solid beep ON - Uncomment if you want a solid beep
                BUZZER.off() 
            
            success, message = start_script('main') 
            
            if success:
                print(f"[AUTO-START SUCCESS] {message}")
            else:
                print(f"[AUTO-START FAILURE] {message}")
            
            current_time_in_cycle = 0.0 # Reset fluid state
            time.sleep(5) 
            
        elif time_remaining <= COUNTDOWN_START: 
            # --- FLUID COUNTDOWN BEEPING (60s to 0s) ---
            
            # 1. Calculate the normalized time (0.0 at 60s, 1.0 at 0s)
            normalized_time = 1.0 - (time_remaining / COUNTDOWN_START)
            
            # 2. Map normalized time to a smoothly increasing frequency
            freq_range = MAX_FREQ - MIN_FREQ
            # Calculated frequency accelerates from 0.2Hz to 8.0Hz
            beep_frequency = max(MIN_FREQ + (normalized_time * freq_range), 0.05) # Ensure a small floor
            
            # 3. Calculate the full period (time for one beep ON + one beep OFF)
            period = 1.0 / beep_frequency
            half_period = period / 2.0
            
            # 4. Update the time within the current beep/pause cycle
            current_time_in_cycle += CYCLE_TIME
            
            # 5. Determine the Buzzer State
            if BUZZER_AVAILABLE:
                # The pulse duration (ON time) is set to half the period for a 50% duty cycle
                if current_time_in_cycle < half_period:
                    BUZZER.on() 
                else:
                    BUZZER.off()

                # 6. Cycle Wrap-around Check
                if current_time_in_cycle >= period:
                    current_time_in_cycle = 0.0
            
            # Wait for the fixed cycle time before repeating
            time.sleep(CYCLE_TIME)


@app.before_request
def update_last_connection_time():
    """Hook runs before every request to reset the auto-start timer and ensure a clean state."""
    global LAST_CONNECTION_TIME
    
    if not is_main_controller_active():
        # Reset the timer
        LAST_CONNECTION_TIME = time.time()
        
    # Ensure the buzzer is off immediately regardless of timer state, suppressing any unintended sound.
    if BUZZER_AVAILABLE:
        BUZZER.off() 


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
        print("Status: Fluid, accelerating countdown from 60 seconds.")
        print("Reset Behavior: Immediate, clean BUZZER.off() on client request.")
    else:
        print("Buzzer Countdown: INACTIVE (gpiozero not found or failed to initialize).")
    print("------------------------------------------------------------------")
    app.run(host="0.0.0.0", port=5000, debug=False)

