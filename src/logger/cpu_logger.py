# =========================================================================
# The Kabot-1 Mission: CPU Temperature Logger (Flight-Ready)
# =========================================================================
# Logs CPU temperature to CSV and JSON, and emits a heartbeat file so the
# master launcher can detect both crashes and stalls.
# =========================================================================

import time
from datetime import datetime
import os
import json

# --- Configuration Settings ---
FLIGHT_MODE = True  # Silence terminal output during flight

# Data directories
DATA_DIR = os.path.join("src", "logger", "data")
DATA_FILE = os.path.join(DATA_DIR, "CPU_TEMP.txt")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

# Heartbeat directory
HEARTBEAT_DIR = os.path.join("src", "logger", "heartbeats")
HEARTBEAT_FILE = os.path.join(HEARTBEAT_DIR, "cpu_logger.json")

# Store the start time of the script
SCRIPT_START_TIME = datetime.now()

# --- Utility Functions ---

def read_cpu_temp():
    """Reads CPU temperature from system file (in °C)."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.readline().strip()
            return float(temp_str) / 1000.0
    except Exception:
        return None

def write_live_data(data):
    """Update centralized JSON file for dashboard."""
    full_data = {}
    if os.path.exists(LIVE_DATA_FILE):
        try:
            with open(LIVE_DATA_FILE, 'r') as f:
                full_data = json.load(f)
        except Exception:
            pass

    full_data.update({
        "timestamp": data["timestamp"],
        "cpu_temp": data["cpu_temp"]
    })

    try:
        with open(LIVE_DATA_FILE, 'w') as f:
            json.dump(full_data, f, indent=4)
    except Exception as e:
        if not FLIGHT_MODE:
            print(f"Error writing live data JSON: {e}")

def write_heartbeat():
    """Write a heartbeat JSON file with the current timestamp."""
    os.makedirs(HEARTBEAT_DIR, exist_ok=True)
    try:
        with open(HEARTBEAT_FILE, "w") as f:
            json.dump({"last_heartbeat": datetime.now().isoformat()}, f)
    except Exception:
        # Fail silently in flight mode
        pass

# --- Main Functions ---

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,cpu_temp\n")
        except Exception as e:
            if not FLIGHT_MODE:
                print(f"CRITICAL ERROR: Failed to create log file: {e}")
            return

    if not FLIGHT_MODE:
        print(f"Kabot-1 CPU Temp Logger active. Logging to {DATA_FILE}. Press Ctrl+C to stop.")
    main_loop()

def main_loop():
    try:
        while True:
            temperature = read_cpu_temp()
            if temperature is not None:
                timestamp = datetime.now().strftime("%H:%M:%S")
                data_line = f"{timestamp},{temperature:.1f}\n"
                with open(DATA_FILE, "a") as f:
                    f.write(data_line)

                data_point = {
                    "timestamp": timestamp,
                    "cpu_temp": round(temperature, 1)
                }
                write_live_data(data_point)

                # --- Heartbeat update ---
                write_heartbeat()

                if not FLIGHT_MODE:
                    print(f"\rLogged: {timestamp} | CPU Temp: {temperature:.1f}°C", end="", flush=True)
            else:
                if not FLIGHT_MODE:
                    print("\rFailed to read CPU temperature.", end="", flush=True)

            time.sleep(10)

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nLogging terminated.")
            end_time = datetime.now()
            duration = end_time - SCRIPT_START_TIME
            print(f"Total runtime: {duration}")
    except Exception as e:
        if not FLIGHT_MODE:
            print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")

if __name__ == "__main__":
    main()
