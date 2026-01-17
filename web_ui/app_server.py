import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory, request

app = Flask(__name__)

# Base Directory Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path Verification
LOGS_INFLIGHT = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight")
LOGS_BACKUP = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight", "backup")
SCRIPTS_DIR = os.path.join(BASE_DIR, "src", "logger", "scripts")
SIM_DIR = os.path.join(BASE_DIR, "src", "simulation", "scripts")
# Ensure this matches exactly where payload_flight_simulation.py saves mission_sim.mp4
VIDEO_PATH = os.path.join(BASE_DIR, "src", "simulation", "output") 

# Ensure output directory exists to avoid 404s
if not os.path.exists(VIDEO_PATH):
    os.makedirs(VIDEO_PATH, exist_ok=True)

scripts_config = {
    'main_controller': {'title': 'Main Flight Controller', 'script': os.path.join(BASE_DIR, 'main.py')},
    'cpu_logger': {'title': 'CPU Temp Logger', 'script': os.path.join(SCRIPTS_DIR, 'cpu_temp_logger.py'), 'chart_file': 'cpu_temp.txt'},
    'mpu_logger': {'title': 'MPU6050 Logger', 'script': os.path.join(SCRIPTS_DIR, 'mpu6050_logger.py'), 'chart_file': 'MPU6050.txt'},
    'sound_logger': {'title': 'Sound Logger', 'script': os.path.join(SCRIPTS_DIR, 'sound_logger.py'), 'chart_file': 'sound_logger.txt'},
    'simulation': {
        'title': 'Flight Simulation', 
        'script': os.path.join(SIM_DIR, 'payload_flight_simulation.py'), 
        'video_file': 'mission_sim.mp4'
    }
}

RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()

@app.route('/')
def index():
    return render_template('dashboard.html', scripts_config=scripts_config)

@app.route('/api/status')
def get_status():
    with PROCESS_LOCK:
        status = {}
        for key in scripts_config:
            p = RUNNING_PROCESSES.get(key)
            if p:
                if p.poll() is None:
                    status[key] = {"running": True, "pid": p.pid}
                else:
                    status[key] = {"running": False, "pid": None}
                    # We keep the key in memory for one cycle so the UI can detect the "Just Finished" state
            else:
                status[key] = {"running": False, "pid": None}
        return jsonify(status)

@app.route('/api/script/<name>/<action>', methods=['POST'])
def control_script(name, action):
    with PROCESS_LOCK:
        if action == 'start':
            # Clean up old video before starting to ensure no 404 on stale files
            if name == 'simulation':
                old_video = os.path.join(VIDEO_PATH, scripts_config[name]['video_file'])
                if os.path.exists(old_video):
                    try: os.remove(old_video)
                    except: pass

            script_path = scripts_config[name]['script']
            if not os.path.exists(script_path):
                return jsonify({"success": False, "message": f"Script not found: {script_path}"})

            # Detach process
            p = subprocess.Popen(
                ["python3", script_path],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=BASE_DIR # Run from project root to ensure internal paths work
            )
            RUNNING_PROCESSES[name] = p
            return jsonify({"success": True})
            
        elif action == 'stop':
            p = RUNNING_PROCESSES.get(name)
            if p:
                try: os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                except: p.terminate()
                del RUNNING_PROCESSES[name]
            return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/video/<filename>')
def serve_video(filename):
    # This ensures Flask looks in the absolute path
    return send_from_directory(VIDEO_PATH, filename)

# ... (Rest of your log list and download routes remain the same)
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
    return "Not found", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)

