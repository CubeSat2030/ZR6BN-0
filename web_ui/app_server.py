# =========================================================================
# Kabot-1 Mission Control Dashboard Server (OctoPrint Style) - FINAL & PATCHED
# =========================================================================
# FEATURE UPDATE: Implemented Connection Standby Heartbeat (2 rapid beeps/3s).
# =========================================================================

import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
from flask import Flask, render_template, jsonify, send_from_directory, abort

try:
    from gpiozero import Buzzer
    # Initialize Buzzer once at startup
    BUZZER = Buzzer(21) 
    BUZZER_AVAILABLE = True
except ImportError:
    print("[WARNING] gpiozero or RPi.GPIO not available. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False
except Exception as e:
    # Handle cases where GPIO 21 is busy or other initialization errors
    print(f"[WARNING] Could not initialize Buzzer on GPIO 21: {e}. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False


# --- Configuration ---
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent 
MAIN_CONTROLLER_SCRIPT = BASE_DIR / "main.py"

SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger"
PLOT_DIR = SRC_DIR / "plotter"
CHARTS_DIR = PLOT_DIR / "charts"
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- NEW: Global State and Timer Configuration ---
AUTO_START_TIMEOUT = 60 # Seconds
LAST_CONNECTION_TIME = time.time() # Last time a request was received
BUZZER_THREAD_STOP = threading.Event() # Flag to stop the buzzer thread

# --- Flask App Initialization ---
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

RUNNING_PROCESSES = {}

SCRIPTS_CONFIG = {
    "main": {
        "title": "Flight Controller (main.py)",
        "log_script": MAIN_CONTROLLER_SCRIPT, 
        "is_main_controller": True
    },
    "dht": {
        "title": "DHT Sensor Logger",
        "log_script": LOG_DIR / "dht_logger.py",
        "plot_script": PLOT_DIR / "dht_plotter.py",
        "chart_file": "dht_chart.svg"
    },
    "mpu": {
        "title": "MPU-6050 Logger",
        "log_script": LOG_DIR / "mpu6050_logger.py",
        "plot_script": PLOT_DIR / "mpu6050_plotter.py",
        "chart_file": "mpu_chart.svg"
    },
    "sound": {
        "title": "Sound Logger",
        "log_script": LOG_DIR / "sound_logger.py",
        "plot_script": PLOT_DIR / "sound_plotter.py",
        "chart_file": "sound_chart.svg"
    }
}

# =========================================================================
# BUZZER COUNTDOWN AND AUTO-START LOGIC
# =========================================================================

def reset_auto_start_timer():
    """Stops the buzzer and resets the auto-start timer."""
    global LAST_CONNECTION_TIME
    if BUZZER_AVAILABLE:
        # Ensure silence when the timer is reset/active connection is detected
        BUZZER.off() 
    
    if not is_main_controller_active():
        # Reset timer to current time (full timeout remaining)
        LAST_CONNECTION_TIME = time.time() 
        # print(f"[TIMER] Timer reset. Time: {LAST_CONNECTION_TIME}")

def buzzer_double_beep(delay_between_beeps=0.1, total_duration=3.0):
    """Executes the two rapid beeps and waits for the remaining duration."""
    if not BUZZER_AVAILABLE:
        time.sleep(total_duration)
        return
        
    start_wait = time.time()
    
    # Beep 1
    BUZZER.on()
    time.sleep(delay_between_beeps)
    BUZZER.off()
    
    # Short pause
    time.sleep(delay_between_beeps)
    
    # Beep 2
    BUZZER.on()
    time.sleep(delay_between_beeps)
    BUZZER.off()
    
    # Wait for the remaining time (approx 3.0s total cycle)
    remaining_wait = total_duration - (time.time() - start_wait)
    if remaining_wait > 0:
        time.sleep(remaining_wait)


def start_buzzer_countdown():
    """
    Runs in a background thread. Manages the countdown, buzzer beeping, 
    and automatically launches main.py if the timer expires.
    """
    global LAST_CONNECTION_TIME
    global BUZZER_THREAD_STOP
    
    while not BUZZER_THREAD_STOP.is_set():
        
        # Check 1: Is the mission already running?
        if is_main_controller_active():
            if BUZZER_AVAILABLE:
                BUZZER.off()
            # print("[TIMER] Mission running. Countdown thread paused.")
            time.sleep(5)
            continue
            
        time_elapsed = time.time() - LAST_CONNECTION_TIME
        time_remaining = AUTO_START_TIMEOUT - time_elapsed
        
        # Check 2: Has the timer expired? (Launch Mission)
        if time_remaining <= 0:
            print("\n[AUTO-START] Timeout reached. Launching Flight Controller...")
            if BUZZER_AVAILABLE:
                BUZZER.off()
            
            success, message = start_script('main')
            
            if success:
                print(f"[AUTO-START SUCCESS] {message}")
            else:
                print(f"[AUTO-START FAILURE] {message}")
            
            time.sleep(5) 
            
        # Check 3: Is the timer actively counting down?
        elif time_remaining < AUTO_START_TIMEOUT - 5: # Give a 5-second buffer for the Standby state
            
            if time_remaining <= 10:
                # --- FAST BEEP (0-10 seconds remaining) ---
                delay = 0.2
                if BUZZER_AVAILABLE:
                    BUZZER.on()
                time.sleep(delay)
                if BUZZER_AVAILABLE:
                    BUZZER.off()
                time.sleep(delay)
                # print(f"[TIMER] FAST BEEP! Remaining: {time_remaining:.1f}s")
                
            elif time_remaining <= 30:
                # --- MEDIUM BEEP (10-30 seconds remaining) ---
                delay = 0.5
                if BUZZER_AVAILABLE:
                    BUZZER.on()
                time.sleep(delay)
                if BUZZER_AVAILABLE:
                    BUZZER.off()
                time.sleep(delay)
                # print(f"[TIMER] MEDIUM BEEP. Remaining: {time_remaining:.1f}s")

            elif time_remaining < AUTO_START_TIMEOUT - 5:
                # --- SLOW BEEP (30-55 seconds remaining) ---
                delay = 1.0
                if BUZZER_AVAILABLE:
                    BUZZER.on()
                time.sleep(0.1) # Short pulse
                if BUZZER_AVAILABLE:
                    BUZZER.off()
                time.sleep(delay - 0.1)
                # print(f"[TIMER] SLOW BEEP. Remaining: {time_remaining:.1f}s")
            
            # Use the sleep of the last executed block
            time.sleep(0.1) 

        # Check 4: Connection is active / Timer is reset (Standby Heartbeat)
        else: 
            # This triggers when LAST_CONNECTION_TIME was recently reset 
            # and time_remaining is close to the full 60 seconds (e.g., 55s to 60s)
            
            # --- CONNECTION STANDBY HEARTBEAT (2 rapid beeps every 3 seconds) ---
            buzzer_double_beep(delay_between_beeps=0.1, total_duration=3.0)
            # print("[TIMER] STANDBY HEARTBEAT. Connection active.")


@app.before_request
def update_last_connection_time():
    """Hook runs before every request to reset the auto-start timer."""
    # This ensures any connection (UI load, status poll) resets the clock.
    reset_auto_start_timer()


# =========================================================================
# (All other functions, including script control and API routes, remain unchanged)
# =========================================================================

# ... (is_main_controller_active, get_status, start_script, stop_script, run_plotter remain UNCHANGED) ...
# ... (All @app.route functions remain UNCHANGED) ...


if __name__ == "__main__":
    # Start the background thread for auto-start and buzzer countdown
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    # Clean up the buzzer on exit
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
    print(f"Auto-Start Timeout: {AUTO_START_TIMEOUT} seconds.")
    if BUZZER_AVAILABLE:
        print("Buzzer Countdown: ACTIVE on GPIO 21.")
        print("Status: Standby Heartbeat (2 quick beeps/3s) while connected.")
    else:
        print("Buzzer Countdown: INACTIVE (gpiozero not found or failed to initialize).")
    print("------------------------------------------------------------------")
    app.run(host="0.0.0.0", port=5000, debug=False)
