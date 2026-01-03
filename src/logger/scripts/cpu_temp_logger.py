# =========================================================================
# Kabot-1 Mission: CPU Temperature Logger (Flight-Ready with Heartbeat)
# =========================================================================

import time
from datetime import datetime
import os
import json
from heartbeat import write_heartbeat

FLIGHT_MODE = True

DATA_DIR = os.path.join("src", "logger", "data", "2_inflight")
DATA_FILE = os.path.join(DATA_DIR, "cpu_temp.txt")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

SCRIPT_START_TIME = datetime.now()

def read_cpu_temp():
    """Reads CPU temperature from system file (in °C)."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.readline().strip()) / 1000.0
    except Exception:
        return None

def write_live_data(data):
    full_data = {}
    if os.path.exists(LIVE_DATA_FILE):
        try:
            with open(LIVE_DATA_FILE, 'r') as f:
                full_data = json.load(f)
        except Exception:
            pass
    full_data.update(data)
    try:
        with open(LIVE_DATA_FILE, 'w') as f:
            json.dump(full_data, f, indent=4)
    except:
        pass

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("timestamp,cpu_temp\n")

    if not FLIGHT_MODE:
        print(f"CPU Temp Logger active. Logging to {DATA_FILE}.")
    main_loop()

def main_loop():
    try:
        while True:
            temperature = read_cpu_temp()
            if temperature is not None:
                timestamp = datetime.now().strftime("%H:%M:%S")
                with open(DATA_FILE, "a") as f:
                    f.write(f"{timestamp},{temperature:.1f}\n")

                data_point = {"timestamp": timestamp, "cpu_temp": round(temperature, 1)}
                write_live_data(data_point)
                write_heartbeat("cpu_logger.json")

                if not FLIGHT_MODE:
                    print(f"\rLogged: {timestamp} | CPU Temp: {temperature:.1f}°C", end="", flush=True)
            time.sleep(10)

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nCPU Temp logging terminated.")

if __name__ == "__main__":
    main()
