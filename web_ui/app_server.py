# =========================================================================
# Kabot-1 Mission Control Dashboard Server - THREAD-SAFE VERSION
# =========================================================================
# FIX: Added threading.Lock around all access to the global RUNNING_PROCESSES
# dictionary to prevent Internal Server Errors (500) due to race conditions.
#
# NEW FEATURE: Single-Client WebUI Access Control
# =========================================================================

import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
from flask import Flask, render_template, jsonify, send_from_directory, abort, request, redirect, url_for

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
PLOT_DIR = PLOT_DIR / "plotter"
CHARTS_DIR = PLOT_DIR / "charts"
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Global State and Timer Configuration ---
AUTO_START_TIMEOUT = 60 # Seconds
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()

# --- SINGLE-CLIENT ACCESS CONTROL VARIABLES ---
AUTHORIZED_CLIENT_IP = None
LAST_ACTIVE_IP = None # Used to display which IP currently has control
# ----------------------------------------------

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
# BUZZER COUNTDOWN AND AUTO-START LOGIC
# =========================================================================

def reset_auto_start_timer():
    """Stops the buzzer and resets the auto-start timer."""
    global LAST_CONNECTION_TIME
    if BUZZER_AVAILABLE:
        BUZZER.off() 
    
    if not is_main_controller_active():
        LAST_CONNECTION_TIME = time.time() 

def buzzer_double_beep(delay_between_beeps=0.1, total_duration=10.0):
    """Executes the two rapid beeps and waits for the remaining duration."""
    if not BUZZER_AVAILABLE:
        time.sleep(total_duration)
        return
        
    start_wait = time.time()
    
    # Beep 1
    BUZZER.on()
    time.sleep(delay_between_beeps)
    BUZZER.off()
    
    # Short pause
    time.sleep(delay_between_beeps)
    
    # Beep 2
    BUZZER.on()
    time.sleep(delay_between_beeps)
    BUZZER.off()
    
    # Wait for the remaining time
    remaining_wait = total_duration - (time.time() - start_wait)
    if remaining_wait > 0:
        time.sleep(remaining_wait)

def solid_beep(duration=3.0):
    """Executes a single, solid beep for the specified duration."""
    if not BUZZER_AVAILABLE:
        print(f"[BUZZER] Solid beep of {duration}s requested but unavailable.")
        return True
        
    try:
        BUZZER.on()
        time.sleep(duration)
        BUZZER.off()
        return True
    except Exception as e:
        print(f"[BUZZER ERROR] Failed to perform solid beep: {e}")
        return False


def start_buzzer_countdown():
    """
    Runs in a background thread. Manages the countdown, buzzer beeping, 
    and automatically launches main.py if the timer expires.
    """
    global LAST_CONNECTION_TIME
    global BUZZER_THREAD_STOP
    
    while not BUZZER_THREAD_STOP.is_set():
        
        if is_main_controller_active():
            if BUZZER_AVAILABLE:
                BUZZER.off()
            time.sleep(5)
            continue
            
        time_elapsed = time.time() - LAST_CONNECTION_TIME
        time_remaining = AUTO_START_TIMEOUT - time_elapsed
        
        if time_remaining <= 0:
            # --- AUTO-START TRIGGERED: SOLID BEEP FOR 3 SECONDS ---
            print("\n[AUTO-START] Timeout reached. Launching Flight Controller...")
            
            solid_beep(3.0) # Solid beep for 3 seconds
            
            # The start_script call is now thread-safe
            success, message = start_script('main') 
            
            if success:
                print(f"[AUTO-START SUCCESS] {message}")
            else:
                print(f"[AUTO-START FAILURE] {message}")
            
            time.sleep(5) 
            
        elif time_remaining < AUTO_START_TIMEOUT - 5: 
            # --- COUNTDOWN BEEPING ---
            
            if time_remaining <= 10:
                # FAST BEEP
                delay = 0.2
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(delay)
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(delay)
                
            elif time_remaining <= 30:
                # MEDIUM BEEP
                delay = 0.5
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(delay)
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(delay)

            else:
                # SLOW BEEP
                delay = 1.0 
                if BUZZER_AVAILABLE: BUZZER.on()
                time.sleep(0.1) 
                if BUZZER_AVAILABLE: BUZZER.off()
                time.sleep(delay - 0.1)
            
        else: 
            # --- CONNECTION STANDBY HEARTBEAT ---
            buzzer_double_beep(delay_between_beeps=0.1, total_duration=10.0)


@app.before_request
def update_last_connection_time():
    """Hook runs before every request to reset the auto-start timer."""
    # We only reset the timer if the request is from the currently authorized client
    global AUTHORIZED_CLIENT_IP
    if AUTHORIZED_CLIENT_IP == request.remote_addr:
        reset_auto_start_timer()


# =========================================================================
# ACCESS CONTROL LOGIC
# =========================================================================

@app.before_request
def before_request_access_check():
    """
    Enforces single-client access. The first client to access the root page 
    becomes the AUTHORIZED_CLIENT_IP. Subsequent non-authorized clients are 
    redirected to a lockout page.
    """
    global AUTHORIZED_CLIENT_IP
    global LAST_ACTIVE_IP
    
    current_ip = request.remote_addr

    # If the user is trying to access the lock page, let them through
    if request.path == url_for('lockout'):
        return None # Proceed to the lockout page

    # 1. Authorize on first access to the dashboard page ("/")
    if request.path == url_for('index'):
        if AUTHORIZED_CLIENT_IP is None:
            AUTHORIZED_CLIENT_IP = current_ip
            LAST_ACTIVE_IP = current_ip
            print(f"[ACCESS CONTROL] Authorized initial client: {current_ip}")
            return None # Proceed to the dashboard
        
        elif current_ip == AUTHORIZED_CLIENT_IP:
            LAST_ACTIVE_IP = current_ip # Update active IP
            return None # Proceed to the dashboard
            
        else:
            # Block unauthorized client attempting to access the dashboard
            print(f"[ACCESS CONTROL] Unauthorized client {current_ip} blocked from index.")
            return redirect(url_for('lockout'))

    # 2. Block all API/resource access if the current IP is not the authorized one
    # Note: Requests for charts or API status will fail here if unauthorized
    if AUTHORIZED_CLIENT_IP is not None and current_ip != AUTHORIZED_CLIENT_IP:
        # Allow unauthorized users to see charts and API status ONLY if Flight Controller is running.
        # This keeps the telemetry visible to observers.
        if is_main_controller_active():
            print(f"[ACCESS CONTROL] Unauthorized client {current_ip} permitted viewing (Flight Active).")
            return None 
            
        # Block control actions or sensitive requests if not authorized.
        if request.method == 'POST' or request.path.startswith('/api'):
            print(f"[ACCESS CONTROL] Unauthorized client {current_ip} blocked from API/POST.")
            # For API calls, return a 403 response instead of a redirect
            if request.path.startswith('/api'):
                return jsonify({"success": False, "message": f"Access denied. WebUI is currently controlled by {AUTHORIZED_CLIENT_IP}."}), 403
            else:
                return redirect(url_for('lockout'))
                
        # Allow GET access to charts for general viewing
        if request.path.startswith('/chart'):
            return None

    # If authorized or the path is not the index/lockout, proceed
    return None

# =========================================================================
# FLASK API ROUTES
# =========================================================================

@app.route("/lockout")
def lockout():
    """Page displayed when a client attempts to access the UI while another client is authorized."""
    # Note: We use LAST_ACTIVE_IP here as AUTHORIZED_CLIENT_IP might be None
    controller_ip = LAST_ACTIVE_IP if LAST_ACTIVE_IP else "N/A (First client to load will take control)"
    return render_template("lockout.html", controller_ip=controller_ip), 403

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
    # This check is technically redundant due to before_request_access_check,
    # but kept as a redundant safety measure for control actions.
    if AUTHORIZED_CLIENT_IP != request.remote_addr:
        return jsonify({"success": False, "message": f"Access denied. WebUI is currently controlled by {AUTHORIZED_CLIENT_IP}."}), 403
        
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
    # This check is technically redundant due to before_request_access_check
    if AUTHORIZED_CLIENT_IP != request.remote_addr:
        return jsonify({"success": False, "message": f"Access denied. WebUI is currently controlled by {AUTHORIZED_CLIENT_IP}."}), 403

    if is_main_controller_active():
        return jsonify({"success": False, "message": "Flight Controller is active. Cannot generate charts."}), 403
        
    success, message = run_plotter(name)
    return jsonify({"success": success, "message": message})

@app.route('/api/beep/<float:duration>', methods=['POST'])
def api_trigger_beep(duration):
    # This check is technically redundant due to before_request_access_check
    if AUTHORIZED_CLIENT_IP != request.remote_addr:
        return jsonify({"success": False, "message": f"Access denied. WebUI is currently controlled by {AUTHORIZED_CLIENT_IP}."}), 403

    if not BUZZER_AVAILABLE:
        return jsonify({"success": False, "message": "Buzzer hardware is not available."}), 503
    
    # Run beep in a separate thread so the Flask request can complete immediately
    threading.Thread(target=solid_beep, args=(duration,)).start()
    
    return jsonify({"success": True, "message": f"Solid beep triggered for {duration} seconds."})

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
    # This check is technically redundant due to before_request_access_check
    if AUTHORIZED_CLIENT_IP != request.remote_addr:
        return jsonify({"success": False, "message": f"Access denied. WebUI is currently controlled by {AUTHORIZED_CLIENT_IP}."}), 403
        
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
        print("Alarm: Solid beep for 3 seconds before auto-start AND on manual start.")
    else:
        print("Buzzer Countdown: INACTIVE (gpiozero not found or failed to initialize).")
    print("------------------------------------------------------------------")
    app.run(host="0.0.0.0", port=5000, debug=False)
