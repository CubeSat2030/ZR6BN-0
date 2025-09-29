# =========================================================================
# Kabot-1 Mission Control Dashboard Server - AUTO-FALLBACK HOTSPOT
# =========================================================================
# FEATURE: Automatically switches to Hotspot mode if no external network 
# connection is established within 30 seconds of starting.
# =========================================================================

import subprocess
import pathlib
import sys
import time
import signal
import os
import threading
from flask import Flask, render_template, jsonify, send_from_directory, abort

# --- GPIO/Buzzer Initialization (UNCHANGED) ---
try:
    from gpiozero import Buzzer
    BUZZER = Buzzer(21) 
    BUZZER_AVAILABLE = True
except ImportError:
    print("[WARNING] gpiozero or RPi.GPIO not available. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False
except Exception as e:
    print(f"[WARNING] Could not initialize Buzzer on GPIO 21: {e}. Buzzer feature disabled.")
    BUZZER_AVAILABLE = False


# --- Configuration ---
# ... (BASE_DIR, SCRIPTS_CONFIG, etc., are UNCHANGED) ...
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent 
MAIN_CONTROLLER_SCRIPT = BASE_DIR / "main.py"

SRC_DIR = BASE_DIR / "src"
LOG_DIR = SRC_DIR / "logger"
PLOT_DIR = SRC_DIR / "plotter"
CHARTS_DIR = PLOT_DIR / "charts"
TEMPLATES_DIR = BASE_DIR / "web_ui" / "templates"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Global State and Timer Configuration ---
AUTO_START_TIMEOUT = 60 # Seconds (For mission start)
NETWORK_CHECK_TIMEOUT = 30 # Seconds (For Wi-Fi client connection)
LAST_CONNECTION_TIME = time.time()
BUZZER_THREAD_STOP = threading.Event()
WATCHDOG_THREAD_STOP = threading.Event() # NEW: Stop flag for the network check thread

# NEW: State variables
WIFI_MODE = "client" # Start in client mode
NETWORK_CHECK_START_TIME = time.time() 

# --- Flask App Initialization (UNCHANGED) ---
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

RUNNING_PROCESSES = {}
PROCESS_LOCK = threading.Lock() # CRITICAL: Lock for thread safety

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
# SYSTEM PROCESS CHECK & CONTROL FUNCTIONS (UNCHANGED)
# =========================================================================
# (is_main_controller_active, get_status, start_script, stop_script, run_plotter)

# ... (Previous functions are here, unchanged, as they only use the thread-safe PROCESS_LOCK) ...

# =========================================================================
# NEW: WIFI MODE MANAGEMENT FUNCTIONS
# =========================================================================

def get_wifi_mode():
    """Returns the current operational mode of the Pi (Client or Hotspot)."""
    global WIFI_MODE
    return WIFI_MODE

def is_client_connected_to_internet():
    """
    Checks if the Pi has an internet connection by trying to ping a reliable DNS server.
    Only relevant if WIFI_MODE is 'client'.
    """
    if get_wifi_mode() != "client":
        return False
        
    try:
        # Ping Google's DNS server (8.8.8.8) with a timeout of 1 packet/1 second
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', '8.8.8.8'], 
            capture_output=True, 
            check=False
        )
        # Check if the process returned a success code AND if "1 received" is in output
        return result.returncode == 0 and b"1 received" in result.stdout
    except Exception:
        return False

def switch_to_hotspot_mode():
    """Switches network interface wlan0 to Access Point mode."""
    global WIFI_MODE
    try:
        if WIFI_MODE == "hotspot":
            return True, "Already in Hotspot Mode."
            
        print("[NETWORK] Switching to Hotspot Mode...")
        
        # 1. Stop networking services
        subprocess.run(['sudo', 'systemctl', 'stop', 'dhcpcd'], check=False)
        subprocess.run(['sudo', 'systemctl', 'stop', 'wpa_supplicant'], check=False)
        
        # 2. Start Hotspot Services (Requires hostapd/dnsmasq config files to be in place)
        subprocess.run(['sudo', 'systemctl', 'start', 'dnsmasq'], check=True)
        subprocess.run(['sudo', 'systemctl', 'start', 'hostapd'], check=True)
        
        # 3. Apply static IP (If not done by dhcpcd config)
        # This is often critical to ensure the AP comes up correctly.
        subprocess.run(['sudo', 'ip', 'addr', 'flush', 'dev', 'wlan0'], check=True)
        subprocess.run(['sudo', 'ifconfig', 'wlan0', '192.168.4.1'], check=True)
        
        WIFI_MODE = "hotspot"
        print("[NETWORK] Successfully switched to Hotspot Mode.")
        return True, "Switched to Hotspot Mode. Connect to the Kabot-1-Mission-Control network."
    except subprocess.CalledProcessError as e:
        WIFI_MODE = "error"
        return False, f"Failed to switch to Hotspot Mode. Error: {e.stderr.strip()}"
    except Exception as e:
        WIFI_MODE = "error"
        return False, f"An unexpected error occurred during hotspot switch: {str(e)}"

def switch_to_client_mode():
    """Switches network interface wlan0 to Wi-Fi Client mode (for internet)."""
    global WIFI_MODE
    global NETWORK_CHECK_START_TIME # Reset timer when we switch back
    try:
        if WIFI_MODE == "client":
            return True, "Already in Client Mode."
            
        print("[NETWORK] Switching to Client Mode...")
        
        # 1. Stop Hotspot Services
        subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd'], check=False)
        subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'], check=False)
        
        # 2. Restart networking services to pick up client config
        # dhcpcd handles obtaining an IP address and manages wpa_supplicant
        subprocess.run(['sudo', 'systemctl', 'start', 'dhcpcd'], check=True)
        # Force a re-scan and connection attempt
        subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'], check=False)
        
        WIFI_MODE = "client"
        NETWORK_CHECK_START_TIME = time.time() # Start the 30s timer again
        print("[NETWORK] Successfully switched to Client Mode. Checking for internet...")
        return True, "Switched to Client Mode. Pi is attempting to connect to an authenticated network."
    except subprocess.CalledProcessError as e:
        WIFI_MODE = "error"
        return False, f"Failed to switch to Client Mode. Error: {e.stderr.strip()}"
    except Exception as e:
        WIFI_MODE = "error"
        return False, f"An unexpected error occurred during client switch: {str(e)}"


def network_watchdog():
    """
    Background thread that manages the 30-second auto-fallback logic.
    """
    global NETWORK_CHECK_START_TIME
    global WATCHDOG_THREAD_STOP
    
    # Give the system a moment to fully boot and attempt connection
    time.sleep(5) 
    
    while not WATCHDOG_THREAD_STOP.is_set():
        current_mode = get_wifi_mode()
        
        if current_mode == "client":
            time_elapsed = time.time() - NETWORK_CHECK_START_TIME
            
            # Check 1: Did the Pi connect to the internet?
            if is_client_connected_to_internet():
                print(f"[WATCHDOG] Internet connection established. Client Mode is stable.")
                # Wait longer before checking again
                time.sleep(60) 
            
            # Check 2: Has the 30-second timeout expired?
            elif time_elapsed >= NETWORK_CHECK_TIMEOUT:
                print(f"[WATCHDOG] {NETWORK_CHECK_TIMEOUT} seconds elapsed. No internet connection found.")
                switch_to_hotspot_mode()
                # Wait longer since we are now in AP mode
                time.sleep(60) 
                
            else:
                # Still waiting for connection
                # print(f"[WATCHDOG] Waiting for connection... {NETWORK_CHECK_TIMEOUT - time_elapsed:.1f}s remaining.")
                time.sleep(3) 

        elif current_mode == "hotspot":
            # If in hotspot mode, just keep checking periodically.
            time.sleep(10)
            
        else: # error/unknown mode
            time.sleep(5) 


# =========================================================================
# BUZZER COUNTDOWN AND AUTO-START LOGIC (UNCHANGED, but relies on get_wifi_mode)
# =========================================================================
# ... (reset_auto_start_timer, buzzer_double_beep, start_buzzer_countdown are here, UNCHANGED) ...

def reset_auto_start_timer():
    """Stops the buzzer and resets the auto-start timer."""
    global LAST_CONNECTION_TIME
    if BUZZER_AVAILABLE:
        BUZZER.off() 
    
    # Only reset the auto-start timer if we are in a mission-ready state (i.e., not a connection error state)
    if not is_main_controller_active() and get_wifi_mode() != "error":
        LAST_CONNECTION_TIME = time.time() 


def start_buzzer_countdown():
    # ... (Logic is unchanged, relies on is_main_controller_active and the timer logic) ...
    # Note: If the watchdog thread is active, this countdown logic should be fine
    # as the buzzer will be reset/silenced if the Pi is running properly or in AP standby.
    # ... (rest of start_buzzer_countdown) ...

# =========================================================================
# FLASK API ROUTES (UPDATED)
# =========================================================================

@app.before_request
def update_last_connection_time():
    """Hook runs before every request to reset the auto-start timer."""
    reset_auto_start_timer()


@app.route("/api/status", methods=['GET'])
def api_status():
    status = get_status()
    # Now includes the current Wi-Fi status
    status['wifi_mode'] = get_wifi_mode() 
    if status['wifi_mode'] == "client":
        status['client_connected'] = is_client_connected_to_internet()
    return jsonify(status)


@app.route('/api/wifi_mode/<target_mode>', methods=['POST'])
def api_wifi_control(target_mode):
    if target_mode == 'hotspot':
        success, message = switch_to_hotspot_mode()
    elif target_mode == 'client':
        success, message = switch_to_client_mode()
    else:
        return jsonify({"success": False, "message": "Invalid target mode. Use 'hotspot' or 'client'."}), 400
        
    return jsonify({
        "success": success, 
        "message": message, 
        "new_mode": get_wifi_mode()
    })

# ... (All other API routes are UNCHANGED) ...


if __name__ == "__main__":
    # Start the Network Watchdog FIRST
    watchdog_thread = threading.Thread(target=network_watchdog, daemon=True)
    watchdog_thread.start()
    
    # Start the Buzzer Countdown SECOND
    countdown_thread = threading.Thread(target=start_buzzer_countdown, daemon=True)
    countdown_thread.start()
    
    def exit_handler(signum, frame):
        if BUZZER_AVAILABLE:
            BUZZER.off()
        BUZZER_THREAD_STOP.set()
        WATCHDOG_THREAD_STOP.set() # Stop the new thread
        print("\n[CLEANUP] All threads stopped.")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    
    print("------------------------------------------------------------------")
    print("Kabot-1 Mission Control Dashboard is starting...")
    print(f"Initial Wi-Fi Mode: {WIFI_MODE.upper()}. Auto-fallback in {NETWORK_CHECK_TIMEOUT}s.")
    print("------------------------------------------------------------------")
    app.run(host="0.0.0.0", port=5000, debug=False)
