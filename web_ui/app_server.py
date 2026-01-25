import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory, request

# =========================================================================
# Kabot-1 Mission Control Dashboard Server - GPIO PATCHED VERSION
# =========================================================================

app = Flask(__name__)

# Base Directory Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define Project-Specific Paths
LOGS_INFLIGHT = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight")
LOGS_BACKUP = os.path.join(BASE_DIR, "src", "logger", "data", "2_inflight", "backup")
SCRIPTS_DIR = os.path.join(BASE_DIR, "src", "logger", "scripts")
SIM_DIR = os.path.join(BASE_DIR, "src", "simulation", "scripts")
VIDEO_PATH = os.path.join(BASE_DIR, "src", "simulation", "output") 

os.makedirs(VIDEO_PATH, exist_ok=True)

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

RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()
AUTO_START_TIMEOUT = 10
BUZZER_THREAD_STOP = threading.Event()

# --- PATCHED BUZZER LOGIC (Release GPIO after every use) ---
def get_buzzer():
    try:
        from gpiozero import Buzzer
        return Buzzer(4)
    except:
        return None

def buzzer_double_beep():
    bz = get_buzzer()
    if bz:
        try:
            bz.on(); time.sleep(0.1); bz.off(); time.sleep(0.1)
            bz.on(); time.sleep(0.1); bz.off()
        finally:
            bz.close() # CRITICAL: Releases GPIO pin 4 immediately

def start_buzzer_countdown():
    start_time = time.time()
    while not BUZZER_THREAD_STOP.is_set():
        elapsed = time.time() - start_time
        if elapsed < AUTO_START_TIMEOUT - 3:
            buzzer_double_beep()
            time.sleep(10)
        elif elapsed < AUTO_START_TIMEOUT:
            bz = get_buzzer()
            if bz:
                try:
                    bz.on(); time.sleep(3); bz.off()
                finally:
                    bz.close() # Release pin before breaking
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
            if p and p.poll() is None:
                status[key] = {"running": True, "pid": p.pid}
            else:
                status[key] = {"running": False, "pid": None}
        return jsonify(status)

@app.route('/api/script/<name>/<action>', methods=['POST'])
def control_script(name, action):
    with PROCESS_LOCK:
        if action == 'start':
            if name in RUNNING_PROCESSES and RUNNING_PROCESSES[name].poll() is None:
                return jsonify({"success": True, "message": "Already running."})

            if name == 'simulation':
                old_video = os.path.join(VIDEO_PATH, scripts_config[name]['video_file'])
                if os.path.exists(old_video):
                    try: os.remove(old_video)
                    except: pass

            script_path = scripts_config[name]['script']
            p = subprocess.Popen(
                ["python3", script_path],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=BASE_DIR
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

