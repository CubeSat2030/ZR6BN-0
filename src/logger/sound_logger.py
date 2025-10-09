# =========================================================================
# Kabot-1 Mission: Sound Logger (Flight-Ready with Heartbeat)
# =========================================================================

import time
from datetime import datetime
import os
import json
from heartbeat import write_heartbeat
# import sounddevice or microphone library as needed

FLIGHT_MODE = True

DATA_DIR = os.path.join("src", "logger", "data")
DATA_FILE = os.path.join(DATA_DIR, "SOUND.txt")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

SCRIPT_START_TIME = datetime.now()

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
            f.write("timestamp,sound_level\n")

    if not FLIGHT_MODE:
        print(f"Sound Logger active. Logging to {DATA_FILE}.")
    main_loop()

def main_loop():
    try:
        while True:
            # Replace with actual microphone read
            sound_level = 0.0

            timestamp = datetime.now().strftime("%H:%M:%S")
            with open(DATA_FILE, "a") as f:
                f.write(f"{timestamp},{sound_level}\n")

            data_point = {"timestamp": timestamp, "sound_level": sound_level}
            write_live_data(data_point)
            write_heartbeat("sound_logger.json")

            if not FLIGHT_MODE:
                print(f"\rLogged Sound at {timestamp}", end="", flush=True)

            time.sleep(1)  # adjust sampling rate

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nSound logging terminated.")

if __name__ == "__main__":
    main()
