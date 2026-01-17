import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory, request

# =========================================================================
# Kabot-1 Mission Control Dashboard Server - REAL PROJECT STRUCTURE VERSION
# =========================================================================

app = Flask(__name__)

# Base Directory is web_ui/, we need to go up one level to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define Project-Specific Paths based on provided structure
LOGS_INFLIGHT = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight")
LOGS_BACKUP = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight", "backup")
SCRIPTS_DIR = os.path.join(BASE_DIR, "src", "logger", "scripts")
SIM_DIR = os.path.join(BASE_DIR, "src", "simulation", "scripts")
VIDEO_PATH = os.path.join(BASE_DIR, "src", "simulation", "output") # Assuming video lands here

# Configuration updated with correct paths to scripts
scripts_config = {
    'main_controller': {
        'title': 'Main Flight Controller', 
        'script': os.path.join(BASE_DIR, 'main.py')
    },
    'cpu_logger': {
        'title': 'CPU Temp Logger', 
        'script': os.path.join(SCRIPTS_DIR, 'cpu_temp_logger.py'), 
        'chart_file': 'cpu_temp.txt'
    },
    'mpu_logger': {
        'title': 'MPU6050 Logger', 
        'script': os.path.join(SCRIPTS_DIR, 'mpu6050_logger.py'), 
        'chart_file': 'MPU6050.txt'
    },
    'sound_logger': {
        'title': 'Sound Logger', 
        'script': os.path.join(SCRIPTS_DIR, 'sound_logger.py'), 
        'chart_file': 'sound_logger.txt'
    },
    'simulation': {
        'title': 'Flight Simulation', 
        'script': os.path.join(SIM_DIR, 'payload_flight_simulation.py'), 
        'video_file': 'mission_sim.mp4'
    }
}

# Global State
RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()
AUTO_START_TIMEOUT = 10
BUZZER_THREAD_STOP = threading.Event()

# Buzzer Hardware Logic
try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(4)
    BUZZER_AVAILABLE = True
except (ImportError, Exception):
    class MockBuzzer:
        def on(self): pass
        def off(self): pass
    BUZZER = MockBuzzer()
    BUZZER_AVAILABLE = False

def buzzer_double_beep():
    if BUZZER_AVAILABLE:
        BUZZER.on(); time.sleep(0.1); BUZZER.off(); time.sleep(0.1);
        BUZZER.on(); time.sleep(0.1); BUZZER.off()

def start_buzzer_countdown():
    start_time = time.time()
    while not BUZZER_THREAD_STOP.is_set():
        elapsed = time.time() - start_time
        if elapsed < AUTO_START_TIMEOUT - 3:
            buzzer_double_beep()
            time.sleep(10)
        elif elapsed < AUTO_START_TIMEOUT:
            if BUZZER_AVAILABLE: BUZZER.on(); time.sleep(3); BUZZER.off()
            break
        else: break

# --- API ROUTES ---

@app.route('/')
def index():
    return render_template('dashboard.html', scripts_config=scripts_config)

@app.route('/api/list_logs')
def list_logs():
    """Aggregates logs from inflight and backup directories."""
    try:
        all_files = []
        # Search both active and backup inflight folders
        for folder in [LOGS_INFLIGHT, LOGS_BACKUP]:
            if os.path.exists(folder):
                files = [f for f in os.listdir(folder) if f.endswith('.txt')]
                for f in files:
                    full_path = os.path.join(folder, f)
                    all_files.append({
                        "name": f,
                        "folder": "backup" if "backup" in folder else "active",
                        "mtime": os.path.getmtime(full_path)
                    })
        
        # Sort by newest first
        all_files.sort(key=lambda x: x['mtime'], reverse=True)
        return jsonify({"success": True, "files": [f['name'] for f in all_files]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/download/log/<filename>')
def download_log(filename):
    """Checks active then backup folders to serve the file."""
    if os.path.exists(os.path.join(LOGS_INFLIGHT, filename)):
        return send_from_directory(LOGS_INFLIGHT, filename, as_attachment=True)
    elif os.path.exists(os.path.join(LOGS_BACKUP, filename)):
        return send_from_directory(LOGS_BACKUP, filename, as_attachment=True)
    return "File not found", 404

@app.route('/api/script/<name>/<action>', methods=['POST'])
def control_script(name, action):
    with PROCESS_LOCK:
        if action == 'start':
            script_path = scripts_config[name]['script']
            # Using python3 to execute absolute paths
            p = subprocess.Popen(["python3", script_path])
            RUNNING_PROCESSES[name] = p
            return jsonify({"success": True, "message": f"{name} started."})
        elif action == 'stop':
            p = RUNNING_PROCESSES.get(name)
            if p:
                p.terminate()
                del RUNNING_PROCESSES[name]
            return jsonify({"success": True, "message": f"{name} stopped."})
    return jsonify({"success": False, "message": "Action failed."})

@app.route('/api/control/wipe_data', methods=['POST'])
def wipe_data():
    """Wipes logs from both active and backup inflight directories."""
    try:
        count = 0
        for folder in [LOGS_INFLIGHT, LOGS_BACKUP]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.endswith('.txt'):
                        os.remove(os.path.join(folder, f))
                        count += 1
        return jsonify({"success": True, "message": f"Wiped {count} log files."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/status')
def get_status():
    with PROCESS_LOCK:
        status = {}
        for key in scripts_config:
            p = RUNNING_PROCESSES.get(key)
            status[key] = {"running": p.poll() is None if p else False, "pid": p.pid if p else None}
        return jsonify(status)

if __name__ == "__main__":
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    def exit_handler(signum, frame):
        if BUZZER_AVAILABLE: BUZZER.off()
        BUZZER_THREAD_STOP.set()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    
    app.run(host='0.0.0.0', port=5000, threaded=True)

