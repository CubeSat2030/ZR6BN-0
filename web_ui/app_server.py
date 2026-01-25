import os
import sys
import time
import signal
import subprocess
import threading
from flask import Flask, render_template, jsonify, send_from_directory

# =========================================================================
# Kabot-1 Mission Control - Stateless GPIO Management
# =========================================================================

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ... [Paths remain the same] ...
SCRIPTS_DIR = os.path.join(BASE_DIR, "src", "logger", "scripts")
# ... [Scripts config remains the same] ...

RUNNING_PROCESSES = {}
LAST_ERRORS = {}
PROCESS_LOCK = threading.Lock()
BUZZER_THREAD_STOP = threading.Event()

# --- STATELESS BUZZER LOGIC ---
# We do NOT keep a global BUZZER object. Every beep is a fresh connection.
def quick_beep(duration=0.1):
    try:
        from gpiozero import Buzzer
        bz = Buzzer(4)
        bz.on()
        time.sleep(duration)
        bz.off()
        bz.close() # CRITICAL: Releases the pin back to the OS immediately
    except Exception as e:
        print(f"Buzzer Busy: {e}")

def start_buzzer_countdown():
    """Background thread for the initial pre-launch countdown."""
    print("Buzzer Thread: Starting pre-launch signaling...")
    start_time = time.time()
    while not BUZZER_THREAD_STOP.is_set():
        elapsed = time.time() - start_time
        if elapsed < 30: # Only beep for the first 30 seconds of server life
            quick_beep(0.1)
            time.sleep(0.1)
            quick_beep(0.1)
            time.sleep(10)
        else:
            print("Buzzer Thread: Countdown complete. Releasing GPIO 4 permanently.")
            break

# --- API ROUTES ---

@app.route('/api/buzzer/off', methods=['POST'])
def kill_server_buzzer():
    """Explicitly stops the server's background buzzer thread to free GPIO 4."""
    BUZZER_THREAD_STOP.set()
    return jsonify({"success": True, "message": "Server buzzer thread terminated. GPIO 4 free."})

@app.route('/api/status')
def get_status():
    with PROCESS_LOCK:
        status = {}
        for key in ['main_controller', 'cpu_logger', 'mpu_logger', 'sound_logger', 'simulation']:
            p = RUNNING_PROCESSES.get(key)
            is_running = p is not None and p.poll() is None
            status[key] = {
                "running": is_running,
                "error": LAST_ERRORS.get(key) if not is_running else None
            }
        return jsonify(status)

@app.route('/api/script/<name>/<action>', methods=['POST'])
def control_script(name, action):
    # Before starting sound_logger, we ensure the server's internal buzzer thread is dead
    if name == 'sound_logger' and action == 'start':
        BUZZER_THREAD_STOP.set()
        time.sleep(0.5) # Let the thread exit

    with PROCESS_LOCK:
        if action == 'start':
            script_path = os.path.join(BASE_DIR, "main.py") if name == 'main_controller' else \
                          os.path.join(SCRIPTS_DIR, f"{name}.py")
            
            try:
                # Use -u for unbuffered stderr so we catch the crash immediately
                p = subprocess.Popen(
                    ["python3", "-u", script_path],
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                    cwd=BASE_DIR
                )
                RUNNING_PROCESSES[name] = p
                # Background thread to catch the error message if it crashes
                def monitor():
                    err = p.stderr.read().decode()
                    if err: LAST_ERRORS[name] = err
                threading.Thread(target=monitor, daemon=True).start()
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})

        elif action == 'stop':
            p = RUNNING_PROCESSES.get(name)
            if p:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                del RUNNING_PROCESSES[name]
            return jsonify({"success": True})

# ... [Include other routes: list_logs, download_log, etc.] ...

if __name__ == "__main__":
    # Force kill the buzzer thread on start
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    app.run(host='0.0.0.0', port=5000, threaded=True)

