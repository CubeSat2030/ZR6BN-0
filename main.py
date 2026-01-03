# =========================================================================
# Kabot I Mission Master Launcher (main.py) - SELF-HEALING + HEARTBEATS + LOGGING
# =========================================================================

import subprocess
import time
import os
import os.path
import signal
import sys
import json
import logging
from datetime import datetime, timedelta

# --- Configuration ---

LOGGING_PROCESSES = [
#    ("CPU Temp Logger", "src/logger/scripts/cpu_logger.py", "src/logger/heartbeats/cpu_logger.json"),
    ("MPU Logger", "src/logger/scripts//mpu6050_logger.py", "src/logger/heartbeats/mpu_logger.json"),
    ("Sound Logger", "src/logger/scripts/sound_logger.py", "src/logger/heartbeats/sound_logger.json"),
]

DETACHED_PROCESSES = [
    ("Web Server", "web_ui/app_server.py"),
]

HEARTBEAT_TIMEOUT = 30  # seconds before a process is considered stalled
STATUS_FILE = os.path.join("src", "logger", "data", "LATEST_SYSTEM_STATUS.json")

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("mission_master.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def update_status(processes, restart_info):
    """Write current system status to JSON file."""
    status = {}
    for name, proc, script_path, hb_file in processes:
        state = "stopped" if proc.poll() is not None else "running"
        last_hb = None
        if os.path.exists(hb_file):
            try:
                with open(hb_file, "r") as f:
                    hb_data = json.load(f)
                last_hb = hb_data.get("last_heartbeat")
            except Exception:
                pass
        status[name] = {
            "pid": proc.pid if proc.poll() is None else None,
            "state": state,
            "last_heartbeat": last_hb,
            "restarts": restart_info[name]["restarts"]
        }
    try:
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to update system status JSON: {e}")

def launch_processes():
    running_loggers = []
    launch_failed = False
    
    logging.info("--- Kabot I Mission Control Startup ---")
    
    try:
        DEVNULL = open(os.devnull, 'w')
    except Exception as e:
        logging.critical(f"Could not open os.devnull: {e}")
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # --- Launch Logging Processes ---
    logging.info(f"Launching {len(LOGGING_PROCESSES)} critical logger processes...")
    for name, script_path, hb_file in LOGGING_PROCESSES:
        full_script_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_script_path):
            logging.critical(f"Script not found: {script_path}.")
            launch_failed = True
            continue 
            
        try:
            command = ["python3", script_path]
            process = subprocess.Popen(
                command, stdout=DEVNULL, stderr=DEVNULL, cwd=project_root
            )
            running_loggers.append((name, process, script_path, hb_file))
            logging.info(f"[SUCCESS] Launched {name} (PID: {process.pid})")
            time.sleep(0.5) 
        except Exception as e:
            logging.critical(f"Failed to launch {name}: {e}")
            launch_failed = True

    # --- Launch Detached Processes ---
    logging.info(f"Launching {len(DETACHED_PROCESSES)} detached processes...")
    for name, script_path in DETACHED_PROCESSES:
        full_script_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_script_path):
            logging.critical(f"Script not found: {script_path}.")
            continue 
        try:
            command = ["python3", script_path]
            subprocess.Popen(command, stdout=DEVNULL, stderr=DEVNULL, cwd=project_root)
            logging.info(f"[SUCCESS] Launched {name} (Detached)")
            time.sleep(0.5) 
        except Exception as e:
            logging.critical(f"Failed to launch {name}: {e}")
            
    if launch_failed or not running_loggers:
        logging.critical("CRITICAL FAILURE: One or more loggers failed to launch. Mission aborted.")
        for name, proc, _, _ in running_loggers:
            if proc.poll() is None:
                try: proc.terminate()
                except: pass
        DEVNULL.close()
    else:
        logging.info("Loggers are active. Web Dashboard: http://<Pi_IP_Address>:5000")
        monitor_processes(running_loggers, DEVNULL, project_root)

def monitor_processes(processes_to_monitor, DEVNULL, project_root):
    restart_info = {name: {"restarts": 0, "next_restart": 0, "script": script}
                    for name, _, script, _ in processes_to_monitor}

    try:
        while True:
            now = time.time()
            for idx, (name, proc, script_path, hb_file) in enumerate(processes_to_monitor):
                # --- Crash Detection ---
                if proc.poll() is not None:
                    logging.warning(f"Logger '{name}' (PID: {proc.pid}) terminated unexpectedly!")
                    restart_logger(name, script_path, idx, processes_to_monitor, restart_info, DEVNULL, project_root)
                    continue

                # --- Heartbeat Detection ---
                if os.path.exists(hb_file):
                    try:
                        with open(hb_file, "r") as f:
                            hb_data = json.load(f)
                        last_hb = datetime.fromisoformat(hb_data["last_heartbeat"])
                        if datetime.now() - last_hb > timedelta(seconds=HEARTBEAT_TIMEOUT):
                            logging.warning(f"Logger '{name}' appears STALLED (no heartbeat in {HEARTBEAT_TIMEOUT}s).")
                            proc.kill()
                            restart_logger(name, script_path, idx, processes_to_monitor, restart_info, DEVNULL, project_root)
                    except Exception:
                        pass
                else:
                    logging.info(f"No heartbeat file for {name} yet.")

            update_status(processes_to_monitor, restart_info)
            time.sleep(5)

    except KeyboardInterrupt:
        logging.info("--- TERMINATION SEQUENCE INITIATED ---")
        for name, proc, _, _ in processes_to_monitor:
            if proc.poll() is None:
                try:
                    proc.send_signal(signal.SIGINT)
                    logging.info(f"[REQUESTED SHUTDOWN] {name} (PID: {proc.pid}). Waiting 2s...")
                    try:
                        proc.wait(timeout=2)
                        logging.info(f"[STOPPED] {name} shut down gracefully.")
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        logging.warning(f"[FORCE KILLED] {name} after timeout.")
                except Exception as e:
                    logging.error(f"Could not terminate {name}: {e}")
        logging.info("Monitored components safely shut down. Web Server remains ACTIVE.")
    finally:
        DEVNULL.close()

def restart_logger(name, script_path, idx, processes_to_monitor, restart_info, DEVNULL, project_root):
    """Helper to restart a crashed or stalled logger with backoff."""
    now = time.time()
    info = restart_info[name]
    if now >= info["next_restart"]:
        backoff = min(60, 2 ** info["restarts"])
        info["restarts"] += 1
        info["next_restart"] = now + backoff
        try:
            command = ["python3", script_path]
            new_proc = subprocess.Popen(command, stdout=DEVNULL, stderr=DEVNULL, cwd=project_root)
            processes_to_monitor[idx] = (name, new_proc, script_path, processes_to_monitor[idx][3])
            logging.info(f"[RECOVERY] Restarted {name} (PID: {new_proc.pid}) "
                         f"after {info['restarts']} attempt(s). Next backoff: {backoff}s")
        except Exception as e:
            logging.critical(f"Failed to restart {name}: {e}")
    else:
        wait_time = int(info["next_restart"] - now)
        logging.info(f"[BACKOFF] {name} restart delayed {wait_time}s.")

if __name__ == "__main__":
    launch_processes()
