# =========================================================================
# Kabot I Mission Master Launcher (main.py)
# =========================================================================
# This script launches all logger processes (monitored) and the Flask 
# web server (detached) concurrently and silently in the background.
#
# CRITICAL: The Web Server is explicitly detached and WILL NOT be terminated
# when this script receives a KeyboardInterrupt (Ctrl+C).
# =========================================================================

import subprocess
import time
import os

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

    # --- Launch Detached Processes (Web UI) ---
    print(f"\nLaunching {len(DETACHED_PROCESSES)} detached processes...")
    for name, script_path in DETACHED_PROCESSES:
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
    
    if running_loggers:
        print("Loggers are active. Web Dashboard: http://<Pi_IP_Address>:5000")
        monitor_processes(running_loggers, DEVNULL)
    else:
        print("No loggers were launched. Mission aborted.")
        DEVNULL.close()

def monitor_processes(processes_to_monitor, DEVNULL):
    """Monitors ONLY the logger processes and cleans them up on keyboard interrupt."""
    try:
        while True:
            # Check for unexpected logger termination
            for name, proc in processes_to_monitor:
                if proc.poll() is not None: 
                    print(f"\n[ALERT] Logger '{name}' (PID: {proc.pid}) has terminated unexpectedly!")
                    
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n--- TERMINATION SEQUENCE INITIATED ---")
        print("Stopping monitored logger processes...")
        
        for name, proc in processes_to_monitor:
            if proc.poll() is None: # Only try to terminate if still running
                try:
                    # Send a terminate signal to all child processes
                    proc.terminate() 
                    print(f"[STOPPED] {name} (PID: {proc.pid})")
                except Exception as e:
                    print(f"[ERROR] Could not terminate {name}: {e}")

        print("\nMonitored components safely shut down.")
        print("NOTE: The Web Server remains ACTIVE in the background.")
        
    finally:
        DEVNULL.close()


if __name__ == "__main__":
    launch_processes()

