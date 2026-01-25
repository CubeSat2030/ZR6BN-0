import os
import sys
import time
import signal
import subprocess
import threading
import io
from flask import Flask, render_template, jsonify, send_from_directory, request

# =========================================================================
# Kabot-1 Mission Control Dashboard Server - ERROR REPORTING VERSION
# =========================================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_INFLIGHT = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight")
LOGS_BACKUP = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight", "backup")
SCRIPTS_DIR = os.path.join(BASE_DIR, "src", "logger", "scripts")
SIM_DIR = os.path.join(BASE_DIR, "src", "simulation", "scripts")
VIDEO_PATH = os.path.join(BASE_DIR, "src", "simulation", "output") 

os.makedirs(VIDEO_PATH, exist_ok=True)

scripts_config = {
    'main_controller': {'title': 'Main Flight Controller', 'script': os.path.join(BASE_DIR, 'main.py')},
    'cpu_logger': {'title': 'CPU Temp Logger', 'script': os.path.join(SCRIPTS_DIR, 'cpu_temp_logger.py'), 'chart_file': 'cpu_temp.txt'},
    'mpu_logger': {'title': 'MPU6050 Logger', 'script': os.path.join(SCRIPTS_DIR, 'mpu6050_logger.py'), 'chart_file': 'MPU6050.txt'},
    'sound_logger': {'title': 'Sound Logger', 'script': os.path.join(SCRIPTS_DIR, 'sound_logger.py'), 'chart_file': 'sound_logger.txt'},
    'simulation': {'title': 'Flight Simulation', 'script': os.path.join(SIM_DIR, 'payload_flight_simulation.py'), 'video_file': 'mission_sim.mp4'}
}

# Global State
RUNNING_PROCESSES = {}
LAST_ERRORS = {} # Stores the last stderr for each script
PROCESS_LOCK = threading.Lock()
AUTO_START_TIMEOUT = 10
BUZZER_THREAD_STOP = threading.Event()

# --- PATCHED BUZZER LOGIC ---
def get_buzzer():
    try:
        from gpiozero import Buzzer
        return Buzzer(4)
    except: return None

def buzzer_double_beep():
    bz = get_buzzer()
    if bz:
        try:
            bz.on(); time.sleep(0.1); bz.off(); time.sleep(0.1)
            bz.on(); time.sleep(0.1); bz.off()
        finally: bz.close()

def start_buzzer_countdown():
    start_time = time.time()
    while not BUZZER_THREAD_STOP.is_set():
        elapsed = time.time() - start_time
        if elapsed < AUTO_START_TIMEOUT - 3:
            buzzer_double_beep(); time.sleep(10)
        elif elapsed < AUTO_START_TIMEOUT:
            bz = get_buzzer()
            if bz:
                try: bz.on(); time.sleep(3); bz.off()
                finally: bz.close()
            break
        else: break

# --- API ROUTES ---

@app.route('/')
def index():
    return render_template('dashboard.html', scripts_config=scripts_config)

@app.route('/api/status')
def get_status():
    with PROCESS_LOCK:
        status = {}
        for key in scripts_config:
            p = RUNNING_PROCESSES.get(key)
            # Check if process exists and is still running
            is_running = p is not None and p.poll() is None
            
            # If it just stopped, we might want to see if it crashed
            error_msg = LAST_ERRORS.get(key) if not is_running else None
            
            status[key] = {
                "running": is_running,
                "pid": p.pid if is_running else None,
                "error": error_msg
            }
        return jsonify(status)

def capture_stderr(name, process):
    """Background thread to capture the last few lines of errors."""
    global LAST_ERRORS
    try:
        # We only capture a bit of data to save RAM
        stderr_data = process.stderr.read(2048)
        if stderr_data:
            with PROCESS_LOCK:
                LAST_ERRORS[name] = stderr_data.decode('utf-8', errors='replace')
    except: pass

@app.route('/api/script/<name>/<action>', methods=['POST'])
def control_script(name, action):
    with PROCESS_LOCK:
        if action == 'start':
            if name in RUNNING_PROCESSES and RUNNING_PROCESSES[name].poll() is None:
                return jsonify({"success": True})

            LAST_ERRORS[name] = None # Clear previous errors
            
            if name == 'simulation':
                old_video = os.path.join(VIDEO_PATH, scripts_config[name]['video_file'])
                if os.path.exists(old_video):
                    try: os.remove(old_video)
                    except: pass

            script_path = scripts_config[name]['script']
            try:
                p = subprocess.Popen(
                    ["python3", "-u", script_path], # -u for unbuffered output
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE, # Capture errors
                    cwd=BASE_DIR
                )
                RUNNING_PROCESSES[name] = p
                # Start a thread to wait for and capture error output if it crashes
                threading.Thread(target=capture_stderr, args=(name, p), daemon=True).start()
                return jsonify({"success": True})
            except Exception as e:
                LAST_ERRORS[name] = str(e)
                return jsonify({"success": False, "message": str(e)})
            
        elif action == 'stop':
            p = RUNNING_PROCESSES.get(name)
            if p:
                try: os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                except: p.terminate()
                del RUNNING_PROCESSES[name]
            return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/list_logs')
def list_logs():
    try:
        all_files = []
        for folder in [LOGS_INFLIGHT, LOGS_BACKUP]:
            if os.path.exists(folder):
                files = [f for f in os.listdir(folder) if f.endswith('.txt')]
                for f in files:
                    full_path = os.path.join(folder, f)
                    all_files.append({"name": f, "mtime": os.path.getmtime(full_path)})
        all_files.sort(key=lambda x: x['mtime'], reverse=True)
        return jsonify({"success": True, "files": [f['name'] for f in all_files]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/download/log/<filename>')
def download_log(filename):
    for folder in [LOGS_INFLIGHT, LOGS_BACKUP]:
        if os.path.exists(os.path.join(folder, filename)):
            return send_from_directory(folder, filename, as_attachment=True)
    return "Log not found", 404

@app.route('/api/download/simulation')
def download_simulation():
    filename = scripts_config['simulation']['video_file']
    if os.path.exists(os.path.join(VIDEO_PATH, filename)):
        return send_from_directory(VIDEO_PATH, filename, as_attachment=True)
    return "Simulation video not found", 404

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_PATH, filename)

@app.route('/api/control/wipe_data', methods=['POST'])
def wipe_data():
    try:
        count = 0
        for folder in [LOGS_INFLIGHT, LOGS_BACKUP]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.endswith('.txt'):
                        os.remove(os.path.join(folder, f)); count += 1
        return jsonify({"success": True, "message": f"Wiped {count} files."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    def exit_handler(signum, frame):
        BUZZER_THREAD_STOP.set()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    app.run(host='0.0.0.0', port=5000, threaded=True)

