#!/usr/bin/env python3
# =========================================================================
# Kabot-1 Mission Control Server
# BACKEND ONLY • UI UNCHANGED • FLIGHT LOCK ENABLED
# =========================================================================

import subprocess
import pathlib
import time
import threading
import signal
import os
import json

from flask import Flask, jsonify, render_template, abort

# =========================================================================
# Optional buzzer (unchanged)
# =========================================================================
try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(21)
    BUZZER_AVAILABLE = True
except Exception:
    BUZZER_AVAILABLE = False

# =========================================================================
# Paths
# =========================================================================
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
LOGGER_DIR = SRC_DIR / "logger"
DATA_DIR = LOGGER_DIR / "data" / "2_inflight"
HEARTBEAT_DIR = LOGGER_DIR / "heartbeats"
SIM_DIR = SRC_DIR / "simulation" / "scripts"

MAIN_SCRIPT = BASE_DIR / "main.py"
DATA_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================================
# Flight Lock (server-side)
# =========================================================================
FLIGHT_STATE_FILE = BASE_DIR / "flight_state.json"

def _load_flight_state():
    if not FLIGHT_STATE_FILE.exists():
        return {"locked": False}
    return json.loads(FLIGHT_STATE_FILE.read_text())

def _set_flight_lock(value: bool):
    FLIGHT_STATE_FILE.write_text(json.dumps({
        "locked": value,
        "timestamp": time.time() if value else None
    }))

def flight_locked() -> bool:
    return _load_flight_state().get("locked", False)

# =========================================================================
# Flask setup
# =========================================================================
app = Flask(__name__, template_folder=str(BASE_DIR / "web_ui" / "templates"))

# =========================================================================
# Process state
# =========================================================================
RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock()

LAST_HEARTBEAT = time.time()
CONNECTION_TIMEOUT = 60  # Dashboard already handles countdown

# =========================================================================
# Script config (matches dashboard JS)
# =========================================================================
SCRIPTS_CONFIG = {
    "main_controller": {
        "title": "Flight Controller",
        "script": MAIN_SCRIPT,
        "main": True
    },
    "cpu": {
        "title": "CPU Logger",
        "script": LOGGER_DIR / "cpu_logger.py"
    },
    "mpu": {
        "title": "MPU-6050 Logger",
        "script": LOGGER_DIR / "mpu6050_logger.py"
    },
    "sound": {
        "title": "Sound Logger",
        "script": LOGGER_DIR / "sound_logger.py"
    },
    "simulation": {
        "title": "Flight Simulation",
        "script": SIM_DIR / "simulate_flight.py",
        "video_file": "simulation.mp4"
    }
}

# =========================================================================
# Utility functions
# =========================================================================
def buzzer_countdown():
    if not BUZZER_AVAILABLE:
        return
    for _ in range(3):
        BUZZER.on()
        time.sleep(0.15)
        BUZZER.off()
        time.sleep(0.15)

def is_process_running(name):
    proc = RUNNING_PROCESSES.get(name)
    return proc and proc.poll() is None

def start_process(name):
    if name not in SCRIPTS_CONFIG:
        raise RuntimeError("Unknown script")
    # Flight lock blocks manual loggers, not main controller
    if flight_locked() and name != "main_controller":
        return False, "Flight lock active"
    script_path = str(SCRIPTS_CONFIG[name]["script"])
    with PROCESS_LOCK:
        if is_process_running(name):
            return False, "Already running"
        proc = subprocess.Popen(
            ["python3", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        RUNNING_PROCESSES[name] = proc
        return True, f"{SCRIPTS_CONFIG[name]['title']} started (PID {proc.pid})"

def stop_process(name):
    with PROCESS_LOCK:
        proc = RUNNING_PROCESSES.get(name)
        if not proc or proc.poll() is not None:
            return False, "Not running"
        proc.terminate()
        proc.wait(timeout=5)
        RUNNING_PROCESSES.pop(name, None)
        return True, f"{SCRIPTS_CONFIG[name]['title']} stopped"

# =========================================================================
# Flask routes
# =========================================================================
@app.route("/")
def index():
    return render_template("dashboard.html", scripts_config=SCRIPTS_CONFIG)

@app.route("/api/status")
def status():
    global LAST_HEARTBEAT
    LAST_HEARTBEAT = time.time()
    status_dict = {}
    for name in SCRIPTS_CONFIG:
        status_dict[name] = {
            "running": is_process_running(name),
            "pid": RUNNING_PROCESSES.get(name).pid if is_process_running(name) else None
        }
    return jsonify(status_dict)

@app.route("/api/script/<name>/<action>", methods=["POST"])
def control_script(name, action):
    if name not in SCRIPTS_CONFIG:
        return jsonify({"success": False, "message": "Unknown script"})
    if action == "start":
        success, msg = start_process(name)
    elif action == "stop":
        success, msg = stop_process(name)
    else:
        success, msg = False, "Unknown action"
    return jsonify({"success": success, "message": msg})

@app.route("/api/simulation/<name>", methods=["POST"])
def generate_simulation(name):
    # Placeholder: simulation video generation
    if name != "simulation":
        return jsonify({"success": False, "message": "Unknown simulation"})
    # Simulate generation delay
    time.sleep(2)
    return jsonify({"success": True, "message": "Simulation generated"})

@app.route("/api/control/<action>", methods=["POST"])
def system_control(action):
    if action == "shutdown":
        _set_flight_lock(True)
        os.system("shutdown now")
        return jsonify({"success": True, "message": "Kabot-1 shutting down"})
    elif action == "reboot":
        _set_flight_lock(True)
        os.system("reboot")
        return jsonify({"success": True, "message": "Kabot-1 rebooting"})
    elif action == "wipe_data":
        # Remove log data
        for f in DATA_DIR.glob("*.txt"):
            f.unlink()
        _set_flight_lock(False)
        return jsonify({"success": True, "message": "All log data wiped"})
    else:
        return jsonify({"success": False, "message": "Unknown system action"})

# =========================================================================
# Heartbeat monitor thread
# =========================================================================
def heartbeat_monitor():
    global LAST_HEARTBEAT
    while True:
        if time.time() - LAST_HEARTBEAT > CONNECTION_TIMEOUT:
            # Lock all processes (server-side) if dashboard disconnected
            for name in RUNNING_PROCESSES:
                if name != "main_controller":
                    stop_process(name)
        time.sleep(1)

threading.Thread(target=heartbeat_monitor, daemon=True).start()

# =========================================================================
# Run server
# =========================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
