# =========================================================================
# Kabot I Mission Master Launcher (main.py) - UPDATED
# =========================================================================
# This script launches all logger processes (monitored) and the Flask 
# web server (detached) concurrently and silently in the background.
#
# CRITICAL: The Web Server is explicitly detached and WILL NOT be terminated
# when this script receives a KeyboardInterrupt (Ctrl+C).
#
# UPDATES:
# 1. Added explicit file existence check before launch.
# 2. Implemented graceful SIGINT/wait/SIGKILL shutdown sequence.
# 3. Implemented 'fail-fast' if any critical logger fails to launch.
# =========================================================================

import subprocess
import time
import os
import os.path
import signal # <-- ADDED for graceful shutdown

# --- Configuration ---

# 1. PROCESSES TO MONITOR AND TERMINATE (Loggers)
# These processes must stop when the main launcher stops.
LOGGING_PROCESSES = [
    ("DHT Logger", "src/logger/dht_logger.py"),
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
    launch_failed = False # <-- ADDED FLAG
    
    print("--- Kabot I Mission Control Startup ---")
    
    # Redirect all stdout/stderr output from subprocesses to null
    try:
        DEVNULL = open(os.devnull, 'w')
    except Exception as e:
        print(f"[ERROR] Could not open os.devnull: {e}")
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # --- Launch Logging Processes (Monitored) ---
    print(f"Launching {len(LOGGING_PROCESSES)} critical logger processes...")
    for name, script_path in LOGGING_PROCESSES:
        
        # Check 1: Script file must exist
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
            running_loggers.append((name, process))
            print(f"[SUCCESS] Launched {name} (PID: {process.pid})")
            time.sleep(0.5) 
        except Exception as e:
            print(f"[CRITICAL FAILURE] Failed to launch {name} ({script_path}): {e}")
            launch_failed = True # <-- SET FLAG

    # --- Launch Detached Processes (Web UI) ---
    print(f"\nLaunching {len(DETACHED_PROCESSES)} detached processes...")
    for name, script_path in DETACHED_PROCESSES:
        
        # Check 2: Script file must exist
        full_script_path = os.path.join(project_root, script_path)
        if not os.path.exists(full_script_path):
            print(f"[CRITICAL FAILURE] Script not found: {script_path}. Check file path.")
            continue 
            
        try:
            command = ["python3", script_path]
            # Launch the Web Server but DO NOT track it for termination.
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
        # If any loggers *did* start, attempt to terminate them now
        for name, proc in running_loggers:
            if proc.poll() is None:
                try:
                    proc.terminate() 
                except:
                    pass
        DEVNULL.close()
    else:
        print("Loggers are active. Web Dashboard: http://<Pi_IP_Address>:5000")
        monitor_processes(running_loggers, DEVNULL)

def monitor_processes(processes_to_monitor, DEVNULL):
    """Monitors ONLY the logger processes and cleans them up on keyboard interrupt."""
    try:
        while True:
            # Check for unexpected logger termination
            for name, proc in processes_to_monitor:
                if proc.poll() is not None: 
                    print(f"\n[ALERT] Logger '{name}' (PID: {proc.pid}) has terminated unexpectedly!")
                    # NOTE: A more advanced version might try to restart the logger here.
                    
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n--- TERMINATION SEQUENCE INITIATED ---")
        print("Stopping monitored logger processes...")
        
        for name, proc in processes_to_monitor:
            if proc.poll() is None: # Only try to terminate if still running
                try:
                    # 1. Send SIGINT (Ctrl+C) for graceful shutdown
                    proc.send_signal(signal.SIGINT)
                    print(f"[REQUESTED SHUTDOWN] {name} (PID: {proc.pid}). Waiting 2s...")
                    
                    # 2. Wait for a short time for graceful exit
                    try:
                        proc.wait(timeout=2)
                        print(f"[STOPPED] {name} (PID: {proc.pid}) shut down gracefully.")
                    except subprocess.TimeoutExpired:
                        # 3. If timeout, force kill
                        proc.kill()
                        print(f"[FORCE KILLED] {name} (PID: {proc.pid}) after timeout.")
                        
                except Exception as e:
                    print(f"[ERROR] Could not terminate {name}: {e}")

        print("\nMonitored components safely shut down.")
        print("NOTE: The Web Server remains ACTIVE in the background.")
        
    finally:
        DEVNULL.close()


if __name__ == "__main__":
    launch_processes()
