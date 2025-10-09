# =========================================================================
# Kabot I Mission Master Launcher (main.py) - UPDATED WITH SELF-HEALING
# =========================================================================
# This script launches all logger processes (monitored) and the Flask 
# web server (detached) concurrently and silently in the background.
#
# Features:
# 1. Explicit file existence check before launch.
# 2. Graceful SIGINT/wait/SIGKILL shutdown sequence.
# 3. Fail-fast if any critical logger fails to launch.
# 4. Self-healing: automatically restarts crashed loggers with exponential backoff.
# =========================================================================

import subprocess
import time
import os
import os.path
import signal
import sys

# --- Configuration ---

# 1. PROCESSES TO MONITOR AND TERMINATE (Loggers)
# These processes must stop when the main launcher stops.
LOGGING_PROCESSES = [
    ("CPU Temp Logger", "src/logger/cpu_logger.py"),
    ("MPU Logger", "src/logger/mpu6050_logger.py"),
    ("Sound Logger", "src/logger/sound_logger.py"),
]

# 2. PROCESSES TO DETACH (Web UI)
# This process must remain running if the main launcher stops or the terminal is closed.
DETACHED_PROCESSES = [
    ("Web Server", "web_ui/app_server.py"),
]

def launch_processes():
    """Launches all configured processes concurrently."""
    
    running_loggers = []
    launch_failed = False
    
    print("--- Kabot I Mission Control Startup ---")
    
    try:
        DEVNULL = open(os.devnull, 'w')
    except Exception as e:
        print(f"[ERROR] Could not open os.devnull: {e}")
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # --- Launch Logging Processes (Monitored) ---
    print(f"Launching {len(LOGGING_PROCESSES)} critical logger processes...")
    for name, script_path in LOGGING_PROCESSES:
        full_script_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_script_path):
            print(f"[CRITICAL FAILURE] Script not found: {script_path}. Check file path.")
            launch_failed = True
            continue 
            
        try:
            command = ["python3", script_path]
            process = subprocess.Popen(
                command, 
                stdout=DEVNULL, 
                stderr=DEVNULL, 
                cwd=project_root 
            )
            running_loggers.append((name, process, script_path))
            print(f"[SUCCESS] Launched {name} (PID: {process.pid})")
            time.sleep(0.5) 
        except Exception as e:
            print(f"[CRITICAL FAILURE] Failed to launch {name} ({script_path}): {e}")
            launch_failed = True

    # --- Launch Detached Processes (Web UI) ---
    print(f"\nLaunching {len(DETACHED_PROCESSES)} detached processes...")
    for name, script_path in DETACHED_PROCESSES:
        full_script_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_script_path):
            print(f"[CRITICAL FAILURE] Script not found: {script_path}. Check file path.")
            continue 
            
        try:
            command = ["python3", script_path]
            subprocess.Popen(
                command, 
                stdout=DEVNULL, 
                stderr=DEVNULL, 
                cwd=project_root 
            )
            print(f"[SUCCESS] Launched {name} (Detached)")
            time.sleep(0.5) 
        except Exception as e:
            print(f"[CRITICAL FAILURE] Failed to launch {name} ({script_path}): {e}")
            
    print("\n--- System Status ---")
    
    # --- FAIL-FAST CHECK ---
    if launch_failed or not running_loggers:
        print("CRITICAL FAILURE: One or more loggers failed to launch. Mission aborted.")
        for name, proc, _ in running_loggers:
            if proc.poll() is None:
                try:
                    proc.terminate() 
                except:
                    pass
        DEVNULL.close()
    else:
        print("Loggers are active. Web Dashboard: http://<Pi_IP_Address>:5000")
        monitor_processes(running_loggers, DEVNULL, project_root)

def monitor_processes(processes_to_monitor, DEVNULL, project_root):
    """Monitors logger processes, restarts them if they crash, and cleans them up on shutdown."""
    restart_info = {name: {"restarts": 0, "next_restart": 0, "script": script}
                    for name, _, script in processes_to_monitor}

    try:
        while True:
            now = time.time()
            for idx, (name, proc, script_path) in enumerate(processes_to_monitor):
                if proc.poll() is not None:  # Process has exited
                    print(f"\n[ALERT] Logger '{name}' (PID: {proc.pid}) terminated unexpectedly!")

                    info = restart_info[name]
                    if now >= info["next_restart"]:
                        backoff = min(60, 2 ** info["restarts"])  # cap at 60s
                        info["restarts"] += 1
                        info["next_restart"] = now + backoff

                        try:
                            command = ["python3", script_path]
                            new_proc = subprocess.Popen(
                                command,
                                stdout=DEVNULL,
                                stderr=DEVNULL,
                                cwd=project_root
                            )
                            processes_to_monitor[idx] = (name, new_proc, script_path)
                            print(f"[RECOVERY] Restarted {name} (PID: {new_proc.pid}) "
                                  f"after {info['restarts']} attempt(s). Next backoff: {backoff}s")
                        except Exception as e:
                            print(f"[CRITICAL] Failed to restart {name}: {e}")
                    else:
                        wait_time = int(info["next_restart"] - now)
                        print(f"[BACKOFF] {name} restart delayed {wait_time}s (stability protection).")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n--- TERMINATION SEQUENCE INITIATED ---")
        print("Stopping monitored logger processes...")

        for name, proc, _ in processes_to_monitor:
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

if __name__ == "__main__":
    launch_processes()
