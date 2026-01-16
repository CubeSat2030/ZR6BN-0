#!/usr/bin/env python3
"""
app_server.py – Kabot-1 Flight Control & Raw Logs Server
--------------------------------------------------------
- Serves the single-page dashboard.
- Flight Controller start/stop (main.py).
- Manual logger scripts.
- Heartbeat and buzzer countdown.
- Raw log file preview/download instead of charts.
"""

import os
import json
import subprocess
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, abort, render_template, request

app = Flask(__name__, template_folder="templates")
LOG_DIR = "logs"
SCRIPTS_DIR = "scripts"

# --- In-memory status store ---
STATUS = {
    "main_controller": {"running": False, "pid": None},
    "scripts": {},  # e.g., "mpu_logger": {"running": False, "pid": 1234}
    "locked": False,
    "locked_at": None
}

# --- Helper Functions ---
def run_script(script_path):
    """Run a script in background and return the Popen object."""
    return subprocess.Popen(["python3", script_path])

def update_main_controller(action):
    if action == "start" and not STATUS["main_controller"]["running"]:
        proc = run_script(os.path.join(SCRIPTS_DIR, "main.py"))
        STATUS["main_controller"] = {"running": True, "pid": proc.pid}
    elif action == "stop" and STATUS["main_controller"]["running"]:
        try:
            os.kill(STATUS["main_controller"]["pid"], 9)
        except:
            pass
        STATUS["main_controller"] = {"running": False, "pid": None}

def is_locked():
    return STATUS["locked"]

def lock_flight():
    STATUS["locked"] = True
    STATUS["locked_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# --- Flask Routes ---

@app.route("/")
def dashboard():
    """
    Render the single-page dashboard HTML
    """
    scripts_config = {}
    # detect .py loggers in scripts directory
    for f in os.listdir(SCRIPTS_DIR):
        if f.endswith(".py") and f != "main.py":
            scripts_config[f[:-3]] = {"title": f[:-3], "script_file": f}
    return render_template("dashboard.html", scripts_config=scripts_config)

# --- API: Main Controller ---
@app.route("/api/script/main_controller/<action>", methods=["POST"])
def api_main_controller(action):
    try:
        update_main_controller(action)
        return jsonify({"success": True, "message": f"Main Controller {action}ed."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- API: Manual Logger Scripts ---
@app.route("/api/script/<name>/<action>", methods=["POST"])
def api_manual_logger(name, action):
    script_path = os.path.join(SCRIPTS_DIR, f"{name}.py")
    if not os.path.exists(script_path):
        return jsonify({"success": False, "message": "Script not found."}), 404

    try:
        if action == "start":
            proc = run_script(script_path)
            STATUS["scripts"][name] = {"running": True, "pid": proc.pid}
        elif action == "stop":
            if name in STATUS["scripts"] and STATUS["scripts"][name]["running"]:
                try:
                    os.kill(STATUS["scripts"][name]["pid"], 9)
                except:
                    pass
                STATUS["scripts"][name] = {"running": False, "pid": None}
        else:
            return jsonify({"success": False, "message": "Unknown action."}), 400
        return jsonify({"success": True, "message": f"Script {name} {action}ed."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# --- API: Status ---
@app.route("/api/status")
def api_status():
    resp = {"main_controller": STATUS["main_controller"]}
    for name, s in STATUS["scripts"].items():
        resp[name] = s
    resp["locked"] = STATUS["locked"]
    resp["locked_at"] = STATUS["locked_at"]
    return jsonify(resp)

# --- API: Flight Lock State ---
@app.route("/api/state")
def api_state():
    return jsonify({"locked": STATUS["locked"], "locked_at": STATUS["locked_at"]})

# --- API: Logs Listing ---
@app.route("/api/logs")
def api_logs():
    try:
        files = [f for f in os.listdir(LOG_DIR) if f.endswith(".txt")]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"files": [], "error": str(e)}), 500

# --- API: Logs Preview ---
@app.route("/api/logs/preview/<filename>")
def api_logs_preview(filename):
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        abort(404)
    with open(filepath, "r") as f:
        content = f.read(10000)  # limit preview
        truncated = os.path.getsize(filepath) > 10000
    return jsonify({"content": content, "truncated": truncated})

# --- API: Logs Download ---
@app.route("/download/log/<filename>")
def download_log(filename):
    return send_from_directory(LOG_DIR, filename, as_attachment=True)

# --- API: System Control ---
@app.route("/api/control/<action>", methods=["POST"])
def api_control(action):
    # For simplicity, shutdown/reboot just respond with success
    if action == "shutdown":
        return jsonify({"success": True, "message": "System shutting down…"})
    elif action == "reboot":
        return jsonify({"success": True, "message": "System rebooting…"})
    elif action == "wipe_data":
        # remove all .txt files
        for f in os.listdir(LOG_DIR):
            if f.endswith(".txt"):
                os.remove(os.path.join(LOG_DIR, f))
        return jsonify({"success": True, "message": "All log data wiped."})
    return jsonify({"success": False, "message": "Unknown system action."}), 400

# --- Background: Buzzer & Heartbeat (simplified) ---
def heartbeat_thread():
    while True:
        time.sleep(2)
        # here you could implement actual buzzer logic
        # for now we just update in-memory heartbeat
        STATUS["heartbeat"] = time.time()

threading.Thread(target=heartbeat_thread, daemon=True).start()

# --- Run Flask App ---
if __name__ == "__main__":
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
