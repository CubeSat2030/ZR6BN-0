#!/usr/bin/env python3
# ============================================================================
# Kabot-1 Mission Control Server
# NO PLOTTER • FLIGHT LOCK ENABLED • HEARTBEAT SAFE
# ============================================================================

import subprocess
import pathlib
import time
import threading
import signal
import json
import os

from flask import Flask, jsonify, render_template, abort, send_from_directory

# ============================================================================
# OPTIONAL BUZZER (UNCHANGED)
# ============================================================================

try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(21)
    BUZZER_AVAILABLE = True
except Exception:
    BUZZER_AVAILABLE = False


# ============================================================================
# PATHS
# ============================================================================

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
LOGGER_DIR = SRC_DIR / "logger"
DATA_DIR = LOGGER_DIR / "data" / "2_inflight"
HEARTBEAT_DIR = LOGGER_DIR / "heartbeats"

TEMPLATE_DIR = BASE_DIR / "web_ui" / "templates"
MAIN_SCRIPT = BASE_DIR / "main.py"

FLIGHT_STATE_FILE = BASE_DIR / "flight_state.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# FLASK
# ============================================================================

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

# ============================================================================
# FLIGHT LOCK STATE
# ============================================================================

def load_flight_state():
    if not FLIGHT_STATE_FILE.exists():
        return {"locked": False, "locked_at": None}
    return json.loads(FLIGHT_STATE_FILE.read_text())

def save_flight_state(locked: bool):
    FLIGHT_STATE_FILE.write_text(json.dumps({
        "locked": locked,
        "locked_at": time.time() if locked else None
    }, indent=2))

def flight_locked():
    return load_flight_state()["locked"]


# ============================================================================
# PROCESS STATE
# ============================================================================

RUNNING = {}
PROCESS_LOCK = threading.Lock()

LAST_HEARTBEAT = time.time()
CONNECTION_TIMEOUT = 60

# ============================================================================
# SCRIPT CONFIG (NO PLOTTERS)
# ============================================================================

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
    }
}

# ============================================================================
# BUZZER COUNTDOWN (UNCHANGED BEHAVIOR)
# ============================================================================

def buzzer_countdown():
    if not BUZZER_AVAILABLE:
        return

    for _ in range(3):
        BUZZER.on()
        time.sleep(0.15)
        BUZZER.off()
        time.sleep(0.15)


# ============================================================================
# PROCESS CONTROL
# ============================================================================

def start_process(name):
    if flight_locked() and not SCRIPTS_CONFIG[name].get("main"):
        raise RuntimeError("Flight lock active")

    with PROCESS_LOCK:
        if name in RUNNING:
            return

        proc = subprocess.Popen(
            ["python3", str(SCRIPTS_CONFIG[name]["script"])],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )
        RUNNING[name] = proc


def stop_process(name):
    with PROCESS_LOCK:
        proc = RUNNING.get(name)
        if not proc:
            return

        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        RUNNING.pop(name, None)


# ============================================================================
# STATUS
# ============================================================================

def collect_status():
    status = {
        "main_controller": {
            "running": "main_controller" in RUNNING
        }
    }

    for name in SCRIPTS_CONFIG:
        if name == "main_controller":
            continue
        status[name] = {
            "running": name in RUNNING
        }

    return status


# ============================================================================
# ROUTES
# ============================================================================

@app.route("/")
def dashboard():
    return render_template("dashboard.html", scripts_config=SCRIPTS_CONFIG)


@app.route("/api/status")
def api_status():
    global LAST_HEARTBEAT
    LAST_HEARTBEAT = time.time()
    return jsonify(collect_status())


@app.route("/api/script/<name>/<action>", methods=["POST"])
def api_script_control(name, action):
    if name not in SCRIPTS_CONFIG:
        abort(404)

    try:
        if action == "start":
            start_process(name)
            return jsonify(success=True, message=f"{name} started")
        elif action == "stop":
            stop_process(name)
            return jsonify(success=True, message=f"{name} stopped")
        else:
            abort(400)
    except RuntimeError as e:
        return jsonify(success=False, message=str(e)), 403


@app.route("/api/script/main_controller/<action>", methods=["POST"])
def api_main_controller(action):
    if action == "start":
        buzzer_countdown()
        save_flight_state(True)
        start_process("main_controller")
        return jsonify(success=True, message="Flight started")
    elif action == "stop":
        stop_process("main_controller")
        save_flight_state(False)
        return jsonify(success=True, message="Flight stopped")
    else:
        abort(400)


# ============================================================================
# RAW LOG ACCESS (READ ONLY)
# ============================================================================

@app.route("/api/logs")
def list_logs():
    return jsonify({
        "files": sorted(f.name for f in DATA_DIR.glob("*.txt"))
    })


@app.route("/api/logs/preview/<filename>")
def preview_log(filename):
    path = DATA_DIR / filename
    if not path.exists():
        abort(404)

    with open(path, "r", errors="replace") as f:
        content = f.read(65536)

    return jsonify(content=content, truncated=path.stat().st_size > 65536)


@app.route("/download/log/<filename>")
def download_log(filename):
    return send_from_directory(DATA_DIR, filename, as_attachment=True)


# ============================================================================
# CONNECTION WATCHDOG
# ============================================================================

def watchdog():
    while True:
        time.sleep(2)
        if time.time() - LAST_HEARTBEAT > CONNECTION_TIMEOUT:
            print("⚠️ Connection heartbeat lost")
            break


threading.Thread(target=watchdog, daemon=True).start()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
