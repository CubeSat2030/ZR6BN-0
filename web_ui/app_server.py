import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory, request

# =========================================================================
# Kabot-1 Mission Control Dashboard Server - THREAD-SAFE VERSION
# =========================================================================
# FAZE OUT NOTICE: Chart generation removed due to RAM constraints (500MB).
# REPLACEMENT: Added .txt file retrieval and local web_ui download system.
# =========================================================================

app = Flask(__name__)

# Constants and Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
# Ensure logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Global State
RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()
AUTO_START_TIMEOUT = 10
BUZZER_THREAD_STOP = threading.Event()

# Mock Buzzer for high-efficiency environments
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
    """Two quick beeps for standby heartbeat."""
    if BUZZER_AVAILABLE:
        BUZZER.on()
        time.sleep(0.1)
        BUZZER.off()
        time.sleep(0.1)
        BUZZER.on()
        time.sleep(0.1)
        BUZZER.off()

def start_buzzer_countdown():
    """Heartbeat and Auto-start countdown logic."""
    start_time = time.time()
    while not BUZZER_THREAD_STOP.is_set():
        elapsed = time.time() - start_time
        if elapsed < AUTO_START_TIMEOUT - 3:
            buzzer_double_beep()
            time.sleep(10)
        elif elapsed < AUTO_START_TIMEOUT:
            if BUZZER_AVAILABLE:
                BUZZER.on()
                time.sleep(3)
                BUZZER.off()
            break
        else:
            break

# --- API ROUTES ---

@app.route('/')
def index():
    # Retaining existing structure, removing chart_file dependency
    return render_template('dashboard.html')

@app.route('/api/list_logs')
def list_logs():
    """Lists all .txt files available for retrieval."""
    try:
        files = [f for f in os.listdir(LOGS_DIR) if f.endswith('.txt')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(LOGS_DIR, x)), reverse=True)
        return jsonify({"status": "success", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/download_log/<filename>')
def download_log(filename):
    """Securely serves txt files for local download."""
    return send_from_directory(LOGS_DIR, filename, as_attachment=True)

@app.route('/api/control', methods=['POST'])
def system_control():
    data = request.json
    action = data.get('action')
    
    with PROCESS_LOCK:
        if action == 'start_mission':
            p = subprocess.Popen(["python3", "mission_logic.py"], stdout=None, stderr=None)
            RUNNING_PROCESSES['mission'] = p
            return jsonify({"status": "success", "message": "Mission started."})
        
        elif action == 'stop_mission':
            p = RUNNING_PROCESSES.get('mission')
            if p:
                p.terminate()
                del RUNNING_PROCESSES['mission']
            return jsonify({"status": "success", "message": "Mission stopped."})
            
        elif action == 'run_simulation':
            # Existing simulation feature preserved
            p = subprocess.Popen(["python3", "simulation_script.py"], stdout=None, stderr=None)
            RUNNING_PROCESSES['simulation'] = p
            return jsonify({"status": "success", "message": "Simulation started."})

        elif action == 'wipe_data':
            # Modified to wipe logs only, charts are phased out
            for f in os.listdir(LOGS_DIR):
                if f.endswith('.txt'):
                    os.remove(os.path.join(LOGS_DIR, f))
            # Preserve cleanup for other media if existing in original logic
            return jsonify({"status": "success", "message": "Mission logs wiped."})

    return jsonify({"status": "error", "message": "Unknown action."})

@app.route('/api/status')
def get_status():
    with PROCESS_LOCK:
        return jsonify({
            "mission_running": 'mission' in RUNNING_PROCESSES,
            "simulation_running": 'simulation' in RUNNING_PROCESSES,
            "buzzer_active": BUZZER_AVAILABLE,
            "timestamp": time.strftime("%H:%M:%S")
        })

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
    print("LOG RETRIEVAL MODE: ACTIVE | CHART GENERATION: PHASED OUT")
    print("------------------------------------------------------------------")
    
    app.run(host='0.0.0.0', port=5000, threaded=True)

