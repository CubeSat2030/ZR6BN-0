import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory, request

# =========================================================================
# Kabot-1 Mission Control Dashboard Server - ERROR REPORTING VERSION
# =========================================================================

app = Flask(__name__)

# Configuration
scripts_config = {
    'main_controller': {'title': 'Main Flight Controller', 'script': 'main_controller.py'},
    'gps_logger': {'title': 'GPS Logger', 'script': 'gps_logger.py', 'chart_file': 'gps_data.txt'},
    'altimeter': {'title': 'Altimeter', 'script': 'altimeter_logger.py', 'chart_file': 'altitude_data.txt'},
    'temp_sensor': {'title': 'Temperature Sensor', 'script': 'temp_logger.py', 'chart_file': 'temp_data.txt'},
    'sound_logger': {'title': 'Sound Logger', 'script': 'sound_logger.py', 'chart_file': 'sound_data.txt'},
    'simulation': {'title': 'Flight Simulation', 'script': 'simulation_script.py', 'video_file': 'mission_sim.mp4'}
}

# Constants and Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Global State
RUNNING_PROCESSES = {}
LAST_ERRORS = {}
PROCESS_LOCK = threading.Lock()
BUZZER_THREAD_STOP = threading.Event()

# --- STATELESS BUZZER LOGIC ---
def quick_beep(duration=0.1):
    """Opens, beeps, and closes GPIO 21 immediately to prevent locking other scripts."""
    try:
        from gpiozero import Buzzer
        bz = Buzzer(21)
        bz.on()
        time.sleep(duration)
        bz.off()
        bz.close() 
    except Exception:
        pass

def start_buzzer_countdown():
    start_time = time.time()
    while not BUZZER_THREAD_STOP.is_set():
        elapsed = time.time() - start_time
        if elapsed < 20: 
            quick_beep(0.1)
            time.sleep(10)
        else: break

# --- API ROUTES ---

@app.route('/')
def index():
    return render_template('dashboard.html', scripts_config=scripts_config)

@app.route('/api/list_logs')
def list_logs():
    try:
        files = [f for f in os.listdir(LOGS_DIR) if f.endswith('.txt')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(LOGS_DIR, x)), reverse=True)
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/download/log/<filename>')
def download_log(filename):
    return send_from_directory(LOGS_DIR, filename, as_attachment=True)

@app.route('/api/script/<name>/<action>', methods=['POST'])
def control_script(name, action):
    # Kill server buzzer if we are starting the mission loggers
    if action == 'start':
        BUZZER_THREAD_STOP.set()

    with PROCESS_LOCK:
        if action == 'start':
            script_file = scripts_config[name]['script']
            try:
                # Start process with stderr piped to capture tracebacks
                p = subprocess.Popen(
                    ["python3", "-u", script_file],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                RUNNING_PROCESSES[name] = p
                LAST_ERRORS[name] = None # Clear previous errors
                
                # Background thread to monitor for crashes
                def monitor(proc, n):
                    _, stderr = proc.communicate()
                    if stderr and proc.returncode != 0:
                        with PROCESS_LOCK:
                            LAST_ERRORS[n] = stderr.strip()
                
                threading.Thread(target=monitor, args=(p, name), daemon=True).start()
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})

        elif action == 'stop':
            p = RUNNING_PROCESSES.get(name)
            if p:
                p.terminate()
                del RUNNING_PROCESSES[name]
            return jsonify({"success": True})
    return jsonify({"success": False, "message": "Action failed."})

@app.route('/api/status')
def get_status():
    with PROCESS_LOCK:
        status = {}
        for key in scripts_config:
            p = RUNNING_PROCESSES.get(key)
            is_running = p.poll() is None if p else False
            status[key] = {
                "running": is_running,
                "pid": p.pid if p else None,
                "error": LAST_ERRORS.get(key) if not is_running else None
            }
        return jsonify(status)

@app.route('/api/control/wipe_data', methods=['POST'])
def wipe_data():
    try:
        for f in os.listdir(LOGS_DIR):
            if f.endswith('.txt'): os.remove(os.path.join(LOGS_DIR, f))
        video_path = os.path.join(BASE_DIR, "mission_sim.mp4")
        if os.path.exists(video_path): os.remove(video_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == "__main__":
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    app.run(host='0.0.0.0', port=5000, threaded=True)

