# =========================================================================
# Kabot-1 Mission Control Dashboard Server - THREAD-SAFE VERSION
# =========================================================================
# FIX: Added threading.Lock around all access to the global RUNNING_PROCESSES
# dictionary to prevent Internal Server Errors (500) due to race conditions.
# FIX: Refactored buzzer logic to be non-blocking and fixed the missing
#      buzzer_double_beep function implementation and auto-start solid beep.
# FIX: Handled KeyError in index() by using .get('chart_file') for simulation script.
# FIX: Enhanced wipe_data_and_charts() to delete data, heartbeats, and media footage.
# FIX: Added dedicated run_simulation function and API route to handle the 
#      non-plotter "simulation" script which generates a video.

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
    BUZZER = Buzzer(4) 
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

# path management
SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger"
# PLOT_DIR = SRC_DIR / "plotter"
SIM_DIR = SRC_DIR / "simulation" / "scripts"
# CHARTS_DIR = PLOT_DIR / "charts" 
TXT_DATA_DIR = LOG_DIR / "data" / "2_inflight" 
FETCH_TXT_FILE_DIR = SRC_DIR / "fetch_data_files" / "scripts"

# Web User INterface dashboard path management.
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

# --- NEW PATHS FOR DATA WIPE ---
DATA_DIR = LOG_DIR / "data" / "3_postflight"
POSTFLIGHT_DATA_DIR = LOG_DIR / "data" / "3_postflight"

HEARTBEATS_DIR = LOG_DIR / "heartbeats"
FOOTAGE_DIR = SRC_DIR / "photography" / "footage"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Global State and Timer Configuration ---
AUTO_START_TIMEOUT = 60 # Seconds
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()
# New global to track the last time a beep happened for the non-blocking loop
LAST_BEEP_TIME = 0 
# New global to track the state of the 3-second solid beep for auto-start
SOLID_BEEP_START_TIME = None

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
        # "plot_script": PLOT_DIR / "cpu_plotter.py",
	"fetch_txt_data_script": FETCH_TXT_FILE_DIR / "fetch_cpu_temp_txt.py"
        # "chart_file": "cpu_chart.svg"
	"fetched_txt_file": "cpu_temp.txt"
    },
    "mpu": {
        "title": "MPU-6050 Logger",
        "log_script": LOG_DIR / "mpu6050_logger.py",
        # "plot_script": PLOT_DIR / "mpu6050_plotter.py",
	"fetch_txt_data_script": FETCH_TXT_FILE_DIR / "fetch_mpu6050_txt.py"
        # "chart_file": "mpu_chart.svg"
	"fetched_txt_file": "mpu6050.txt"
    },
    "simulation": {
        "title": "Payload Flight Simulation",
        "sim_script": SIM_DIR / "payload_flight_simulation.py",
        "video_file": "payload_flight_simulation.mp4"
   },
    "sound": {
        "title": "Sound Logger",
        "log_script": LOG_DIR / "sound_logger.py",
       # "plot_script": PLOT_DIR / "sound_plotter.py",
	"fetch_txt_data_script": FETCH_TXT_FILE_DIR / "fetch_sound_txt.py"
       # "chart_file": "sound_chart.svg"
	"feched_txt_file": "sound.txt" 
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
                "fetched_txt_file": config.get('fetched_txt_file')
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
    # NOTE: The simulation script uses 'sim_script', the loggers use 'log_script'.
    # We prioritize 'log_script' if present, otherwise fall back to 'sim_script'.
    script_path_key = 'log_script' if 'log_script' in config else ('sim_script' if 'sim_script' in config else None)
    
    if not script_path_key:
        return False, f"Configuration for '{name}' is missing a script path (log_script or sim_script)."

    script_path = str(config[script_path_key]) 
    
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
        return False, "Flight Controller (main.py) is running. Fetching of txt logger files is disabled."
        
    if name not in SCRIPTS_CONFIG or 'fetch_txt_data_script' not in SCRIPTS_CONFIG[name]:
        return False, "Unknown or non-plotter script name."
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['fetch_txt_data_script']) 
    chart_file = config['fetched_txt_file']
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=False, 
            cwd=str(BASE_DIR) 
        )
        
        if result.returncode == 0 and os.path.exists(CHARTS_DIR / chart_file):
            return True, f".txt file fetched successfully: {fetched_txt_file}"
        else:
            error_msg = result.stderr.strip() or f"Fetching failed with exit code {result.returncode}."
            return False, f"Fetching failed: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, f"Fetchiing script {name} timed out after 45 seconds."
    except Exception as e:
        return False, f"Failed to run Fetching script {name}: {str(e)}"

# --- NEW FUNCTION FOR SIMULATION VIDEO GENERATION ---
def run_simulation(name):
    """Runs the simulation script synchronously to generate the video."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Simulation is disabled."
        
    if name not in SCRIPTS_CONFIG or 'sim_script' not in SCRIPTS_CONFIG[name]:
        # This will catch the error if the name is correct but sim_script is missing
        return False, "Unknown or non-simulation script name."
    
    config = SCRIPTS_CONFIG[name]
    script_path = str(config['sim_script'])
    video_file = config['video_file']
    
    # Define the output path for the video (same directory as the script)
    video_path = SIM_DIR / video_file
    
    try:
        # Increased timeout to 28800 seconds (480 minutes) for rendering
        print(f"[SIMULATION] Starting video generation for {video_file}...")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=28800, # Time interrupt in seconds.
            cwd=str(BASE_DIR) 
        )
        
        if result.returncode == 0 and os.path.exists(video_path):
            return True, f"Simulation video generated successfully: {video_file}"
        else:
            error_msg = result.stderr.strip() or f"Simulation failed with exit code {result.returncode}."
            return False, f"Simulation failed: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, f"Simulation timed out after 120 minutes."
    except Exception as e:
        return False, f"Failed to run simulation: {str(e)}"
# --- END NEW FUNCTION ---


def wipe_data_and_charts():
    """Deletes all logged data, heartbeats, footage, and charts."""
    if is_main_controller_active():
        return False, "Flight Controller (main.py) is running. Data wipe is disabled."

    success = True
    total_deleted_items = 0
    
    # List of files/patterns to clean
    files_to_clean = [
        (LOG_DIR.glob("*.txt"), "log files in src/logger/"), # Legacy .txt in logger/
        (DATA_DIR.glob("*"), "data files in src/logger/data/"),
        (HEARTBEATS_DIR.glob("*.json"), "heartbeat files in src/logger/heartbeats/"),
    ]
    
    # 1. Delete specific files first
    for file_pattern, desc in files_to_clean:
        try:
            item_count = 0
            for item in file_pattern:
                if item.is_file():
                    os.remove(item)
                    item_count += 1
            total_deleted_items += item_count
            print(f"[DATA WIPE] Deleted {item_count} {desc}")
        except Exception as e:
            success = False
            print(f"[DATA WIPE ERROR] Failed to delete {desc}: {e}")

    # 2. Delete and recreate directories for charts and footage (more robust wipe)
    folders_to_recreate = [
        (CHARTS_DIR, "fetched_data"),
        (FOOTAGE_DIR / "images", "images"),
        (FOOTAGE_DIR / "videos", "videos"),
    ]

    for folder, name in folders_to_recreate:
        try:
            if folder.exists():
                # Count files recursively before deletion
                item_count = len(list(folder.rglob('*'))) 
                shutil.rmtree(folder)
                total_deleted_items += item_count
                print(f"[DATA WIPE] Deleted {item_count} items in {name} directory.")
            
            # Always attempt to recreate the directory for future use
            folder.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            success = False
            print(f"[DATA WIPE ERROR] Failed to delete/recreate {name} directory: {e}")
            
    if success:
        return True, f"Successfully wiped {total_deleted_items} data, heartbeat, media, and chart files."
    else:
        return False, "Wipe completed with errors. Check server logs for details."


# =========================================================================
# BUZZER COUNTDOWN AND AUTO-START LOGIC
# =========================================================================

def reset_auto_start_timer():
    """Stops the buzzer, resets the auto-start timer, and clears the solid beep state."""
    global LAST_CONNECTION_TIME, SOLID_BEEP_START_TIME
    if BUZZER_AVAILABLE:
        BUZZER.off() 
        SOLID_BEEP_START_TIME = None # Clear solid beep state

    if not is_main_controller_active():
        LAST_CONNECTION_TIME = time.time()
        
def double_beep_and_wait(total_duration=10.0, beep_delay=0.1):
    """Executes the two rapid beeps and waits for the remaining duration (non-blocking)."""
    global LAST_BEEP_TIME
    
    if not BUZZER_AVAILABLE:
        # For the non-buzzer case, simply set the last beep time to simulate a completed cycle
        LAST_BEEP_TIME = time.time()
        return

    # Check if a cycle has finished
    if time.time() - LAST_BEEP_TIME >= total_duration:
        start_time = time.time()
        
        # Beep 1
        BUZZER.on()
        time.sleep(beep_delay)
        BUZZER.off()
        
        # Short pause
        time.sleep(beep_delay)
        
        # Beep 2
        BUZZER.on()
        time.sleep(beep_delay)
        BUZZER.off()
        
        # Update LAST_BEEP_TIME based on the start of the cycle
        LAST_BEEP_TIME = start_time
        
    # The countdown thread's main loop handles the required time.sleep(0.1)

def start_buzzer_countdown():
    """
    Runs in a background thread. Manages the countdown, buzzer beeping, 
    and automatically launches main.py if the timer expires.
    
    Uses a polling frequency (0.1s sleep) to avoid blocking the thread
    with long delays.
    """
    global LAST_CONNECTION_TIME, LAST_BEEP_TIME, SOLID_BEEP_START_TIME
    
    # Use a small sleep interval to create a high-frequency polling loop
    LOOP_SLEEP_INTERVAL = 0.1 
    
    while not BUZZER_THREAD_STOP.is_set():
        current_time = time.time()
        
        if is_main_controller_active():
            # If main.py is running, turn off the buzzer and reset times
            if BUZZER_AVAILABLE:
                BUZZER.off()
            SOLID_BEEP_START_TIME = None
            LAST_BEEP_TIME = current_time # Reset heartbeat tracking
            time.sleep(5) # Longer sleep when active
            continue
        
        time_elapsed = current_time - LAST_CONNECTION_TIME
        time_remaining = AUTO_START_TIMEOUT - time_elapsed
        
        # --- AUTO-START TRIGGERED AND SOLID BEEP LOGIC ---
        if time_remaining <= 0:
            if SOLID_BEEP_START_TIME is None:
                # First time hitting timeout: initiate auto-start and solid beep
                print("\n[AUTO-START] Timeout reached. Launching Flight Controller...")
                
                # The start_script call is now thread-safe
                success, message = start_script('main') 
                
                if success:
                    print(f"[AUTO-START SUCCESS] {message}")
                else:
                    print(f"[AUTO-START FAILURE] {message}")
                    
                if BUZZER_AVAILABLE:
                    BUZZER.on() # Solid beep ON
                    SOLID_BEEP_START_TIME = current_time
                    
            # Keep solid beep on for 3 seconds
            if SOLID_BEEP_START_TIME is not None and current_time - SOLID_BEEP_START_TIME >= 3.0:
                if BUZZER_AVAILABLE:
                    BUZZER.off() # Solid beep OFF
                    SOLID_BEEP_START_TIME = None # Clear state
            
            time.sleep(LOOP_SLEEP_INTERVAL)
            continue 

        # --- COUNTDOWN/HEARTBEAT BEEPING LOGIC ---
        
        # Determine the period for the beep cycle (off-time + on-time)
        cycle_period = 0.0 # Default to no regular cycle
        if time_remaining <= 5:
            # SUPER SUPER FAST BEEP (0.0625s ON, 0.0625s OFF) = 0.125s cycle
            cycle_period = 0.125
            beep_duration = 0.0625
        elif time_remaining <= 10:
            # SUPER FAST BEEP (0.125s ON, 0.125s OFF) = 0.25s cycle
            cycle_period = 0.25
            beep_duration = 0.125
        elif time_remaining <= 20:
            # FAST BEEP (0.25s ON, 0.25s OFF) = 0.5s cycle
            cycle_period = 0.5
            beep_duration = 0.25
        elif time_remaining <= 30:
            # MEDIUM BEEP (0.5s ON, 0.5s OFF) = 1.0s cycle
            cycle_period = 1.0
            beep_duration = 0.5
        elif time_remaining < AUTO_START_TIMEOUT - 5: 
            # SLOW BEEP (0.1s ON, 0.9s OFF) = 1.0s cycle
            cycle_period = 1.0
            beep_duration = 0.1
        else:
            # CONNECTION STANDBY HEARTBEAT (Double Beep cycle)
            double_beep_and_wait(total_duration=10.0, beep_delay=0.1)
            time.sleep(LOOP_SLEEP_INTERVAL)
            continue
            
        # Execute the regular countdown beep based on the calculated period/duration
        if cycle_period > 0 and BUZZER_AVAILABLE:
            time_since_last_beep = current_time - LAST_BEEP_TIME
            
            # Check if the buzzer should be ON
            if time_since_last_beep < beep_duration:
                BUZZER.on()
            # Check if the buzzer should be OFF
            elif time_since_last_beep < cycle_period:
                BUZZER.off()
            # Check if it's time for the next cycle to start
            else:
                LAST_BEEP_TIME = current_time # Start a new cycle
                BUZZER.on() # Immediately start ON for the new cycle

        time.sleep(LOOP_SLEEP_INTERVAL)


@app.before_request
def update_last_connection_time():
    """Hook runs before every request to reset the auto-start timer."""
    reset_auto_start_timer()


# =========================================================================
# FLASK API ROUTES (PATCHED)
# =========================================================================

@app.route("/")
def index():
    serializable_config = {}
    for key, config in SCRIPTS_CONFIG.items():
        if not config.get('is_main_controller'):
            # PATCH: Safely retrieve 'chart_file' to avoid KeyError for the 'simulation' script
            chart_file = config.get("fetched_txt_file")
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

# --- NEW API ROUTE FOR SIMULATION VIDEO GENERATION ---
@app.route('/api/simulation/<name>', methods=['POST'])
def api_simulation_generate(name):
    """API endpoint to generate the flight simulation video."""
    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller is active. Cannot run simulation."}), 403
        
    success, message = run_simulation(name)
    return jsonify({"success": success, "message": message})
# --- END NEW API ROUTE ---

@app.route("/fetched_txt_file/<path:filename>")
def get_chart_display(filename):
    if ".." in filename or "/" in filename: abort(400)
    return send_from_directory(CHARTS_DIR, filename, as_attachment=False)

# --- NEW ROUTE FOR SERVING SIMULATION VIDEO ---
@app.route("/video/<path:filename>")
def get_video_display(filename):
    """Serves the simulation video from the simulation directory."""
    if ".." in filename or "/" in filename: abort(400)
    # The SIM_DIR is src/simulation
    return send_from_directory(SIM_DIR, filename, as_attachment=False)
# --- END NEW ROUTE ---

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
def api_wipe_data(): 
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


#------------------------------------------------PRESENTATION MODE-----------------------------------------------------------------------------
# This new route is for the presenttion mode.
# Rather than a power point presentation we thought of  something original and innovative we called Presentaion mode:
# What is presentation mode and how will presentation mode work?:
# Presentation mode is when the payload will be used  when presenting our mission report live on 26 November 2025 @ 19:00PM SAST. 
# 
# What is Presentation Mode?
#
# Presentation Mode is an add-on to  the active web_ui interface. 
# Presentation Mode is an entire different web user interface .
#
# How does Presentation Mode work?
#
# PresentationMode.html and Dashboard.html work together as follows:
# Dashboard.html is our PARENT.
# PresentationMode.html is our CHILD.
# 
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#----------------------------------------------------------------------------------------------------------------------------------------------
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
