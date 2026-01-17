import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory, request

# =========================================================================
# Kabot-1 Mission Control Dashboard Server - LOG RETRIEVAL VERSION
# =========================================================================
# FAZE OUT NOTICE: Chart generation removed due to RAM constraints (500MB).
# REPLACEMENT: Added .txt file retrieval and local web_ui download system.
# =========================================================================

app = Flask(__name__)

# Configuration for loggers and scripts (Preserved structure)
scripts_config = {
    'main_controller': {'title': 'Main Flight Controller', 'script': 'main_controller.py'},
    'gps_logger': {'title': 'GPS Logger', 'script': 'gps_logger.py', 'chart_file': 'gps_data.txt'},
    'altimeter': {'title': 'Altimeter', 'script': 'altimeter_logger.py', 'chart_file': 'altitude_data.txt'},
    'temp_sensor': {'title': 'Temperature Sensor', 'script': 'temp_logger.py', 'chart_file': 'temp_data.txt'},
    'simulation': {'title': 'Flight Simulation', 'script': 'simulation_script.py', 'video_file': 'mission_sim.mp4'}
}

# Constants and Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Global State
RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()
AUTO_START_TIMEOUT = 10
BUZZER_THREAD_STOP = threading.Event()

# Buzzer Logic (Preserved)
class MockBuzzer:
    def on(self): pass
    def off(self): pass
    def beep(self, *args, **kwargs): pass

try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(21)
    BUZZER_AVAILABLE = True
except (ImportError, Exception):
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
            if BUZZER_AVAILABLE:
                BUZZER.on(); time.sleep(3); BUZZER.off()
            break
        else: break

# --- API ROUTES ---

@app.route('/')
def index():
    return render_template('dashboard.html', scripts_config=scripts_config)

@app.route('/api/list_logs')
def list_logs():
    """PHASE OUT REPLACEMENT: List available mission text files."""
    try:
        files = [f for f in os.listdir(LOGS_DIR) if f.endswith('.txt')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(LOGS_DIR, x)), reverse=True)
        return jsonify({"status": "success", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/download_log/<filename>')
def download_log(filename):
    """PHASE OUT REPLACEMENT: Download retrieved txt files."""
    return send_from_directory(LOGS_DIR, filename, as_attachment=True)

@app.route('/api/script/<name>/<action>', methods=['POST'])
def control_script(name, action):
    with PROCESS_LOCK:
        if action == 'start':
            script_file = scripts_config[name]['script']
            p = subprocess.Popen(["python3", script_file])
            RUNNING_PROCESSES[name] = p
            return jsonify({"success": True, "message": f"{name} started."})
        elif action == 'stop':
            p = RUNNING_PROCESSES.get(name)
            if p:
                p.terminate()
                del RUNNING_PROCESSES[name]
            return jsonify({"success": True, "message": f"{name} stopped."})
    return jsonify({"success": False, "message": "Action failed."})

@app.route('/api/simulation/<name>', methods=['POST'])
def run_simulation(name):
    # Simulation logic preserved as it is not a "chart"
    with PROCESS_LOCK:
        p = subprocess.Popen(["python3", scripts_config[name]['script']])
        RUNNING_PROCESSES[name] = p
        return jsonify({"success": True, "message": "Simulation sequence initiated."})

@app.route('/api/control/wipe_data', methods=['POST'])
def wipe_data():
    """Modified to clear logs. Chart cleanup removed."""
    try:
        for f in os.listdir(LOGS_DIR):
            if f.endswith('.txt'):
                os.remove(os.path.join(LOGS_DIR, f))
        return jsonify({"success": True, "message": "Mission logs cleared from HAB payload."})
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
    app.run(host='0.0.0.0', port=5000, threaded=True)

