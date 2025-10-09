# =========================================================================
# Kabot I Mission Master Launcher (main.py) - SELF-HEALING + HEARTBEATS
# =========================================================================
# Features:
# 1. Explicit file existence check before launch.
# 2. Graceful SIGINT/wait/SIGKILL shutdown sequence.
# 3. Fail-fast if any critical logger fails to launch.
# 4. Self-healing: automatically restarts crashed loggers with exponential backoff.
# 5. Heartbeat monitoring: detects hung loggers that stop producing data.
# =========================================================================

import subprocess
import time
import os
import os.path
import signal
import sys
import json
from datetime import datetime, timedelta

# --- Configuration ---

LOGGING_PROCESSES = [
    ("CPU Temp Logger", "src/logger/cpu_logger.py", "src/logger/heartbeats/cpu_logger.json"),
    ("MPU Logger", "src/logger/mpu6050_logger.py", "src/logger/heartbeats/mpu_logger.json"),
    ("Sound Logger", "src/logger/sound_logger.py", "src/logger/heartbeats/sound_logger.json"),
]

DETACHED_PROCESSES = [
    ("Web Server", "web_ui/app_server.py"),
]

HEARTBEAT_TIMEOUT = 30  # seconds before a process is considered stalled

def launch_processes():
    running_loggers = []
    launch_failed = False
    
    print("--- Kabot I Mission Control Startup ---")
    
    try:
        DEVNULL = open(os.devnull, 'w')
    except Exception as e:
        print(f"[ERROR] Could not open os.devnull: {e}")
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # --- Launch Logging Processes ---
    print(f"Launching {len(LOGGING_PROCESSES)} critical logger processes...")
    for name, script_path, hb_file in LOGGING_PROCESSES:
        full_script_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_script_path):
            print(f"[CRITICAL FAILURE] Script not found: {script_path}.")
            launch_failed = True
            continue 
            
        try:
            command = ["python3", script_path]
            process = subprocess.Popen(
                command, stdout=DEVNULL, stderr=DEVNULL, cwd=project_root
            )
            running_loggers.append((name, process, script_path, hb_file))
            print(f"[SUCCESS] Launched {name} (PID: {process.pid})")
            time.sleep(0.5) 
        except Exception as e:
            print(f"[CRITICAL FAILURE] Failed to launch {name}: {e}")
            launch_failed = True

    # --- Launch Detached Processes ---
    print(f"\nLaunching {len(DETACHED_PROCESSES)} detached processes...")
    for name, script_path in DETACHED_PROCESSES:
        full_script_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_script_path):
            print(f"[CRITICAL FAILURE] Script not found: {script_path}.")
            continue 
        try:
            command = ["python3", script_path]
            subprocess.Popen(command, stdout=DEVNULL, stderr=DEVNULL, cwd=project_root)
            print(f"[SUCCESS] Launched {name} (Detached)")
            time.sleep(0.5) 
        except Exception as e:
            print(f"[CRITICAL FAILURE] Failed to launch {name}: {e}")
            
    print("\n--- System Status ---")
    
    if launch_failed or not running_loggers:
        print("CRITICAL FAILURE: One or more loggers failed to launch. Mission aborted.")
        for name, proc, _, _ in running_loggers:
            if proc.poll() is None:
                try: proc.terminate()
                except: pass
        DEVNULL.close()
    else:
        print("Loggers are active. Web Dashboard: http://<Pi_IP_Address>:5000")
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
                    print(f"\n[ALERT] Logger '{name}' (PID: {proc.pid}) terminated unexpectedly!")
                    restart_logger(name, script_path, idx, processes_to_monitor, restart_info, DEVNULL, project_root)
                    continue

                # --- Heartbeat Detection ---
                if os.path.exists(hb_file):
                    try:
                        with open(hb_file, "r") as f:
                            hb_data = json.load(f)
                        last_hb = datetime.fromisoformat(hb_data["last_heartbeat"])
                        if datetime.now() - last_hb > timedelta(seconds=HEARTBEAT_TIMEOUT):
                            print(f"\n[ALERT] Logger '{name}' appears STALLED (no heartbeat in {HEARTBEAT_TIMEOUT}s).")
                            proc.kill()
                            restart_logger(name, script_path, idx, processes_to_monitor, restart_info, DEVNULL, project_root)
                    except Exception:
                        pass
                else:
                    print(f"[WARNING] No heartbeat file for {name} yet.")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n--- TERMINATION SEQUENCE INITIATED ---")
        for name, proc, _, _ in processes_to_monitor:
            if proc.poll() is None:
                try:
                    proc.send_signal(signal.SIGINT)
                    print(f"[REQUESTED SHUTDOWN] {name} (PID: {proc.pid}). Waiting 2s...")
                    try:
                        proc.wait(timeout=2)
                        print(f"[STOPPED] {name} shut down gracefully.")
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        print(f"[FORCE KILLED] {name} after timeout.")
                except Exception as e:
                    print(f"[ERROR] Could not terminate {name}: {e}")
        print("\nMonitored components safely shut down.")
        print("NOTE: The Web Server remains ACTIVE in the background.")
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
            print(f"[RECOVERY] Restarted {name} (PID: {new_proc.pid}) "
                  f"after {info['restarts']} attempt(s). Next backoff: {backoff}s")
        except Exception as e:
            print(f"[CRITICAL] Failed to restart {name}: {e}")
    else:
        wait_time = int(info["next_restart"] - now)
        print(f"[BACKOFF] {name} restart delayed {wait_time}s.")

if __name__ == "__main__":
    launch_processes()
