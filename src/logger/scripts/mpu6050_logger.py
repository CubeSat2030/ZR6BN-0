# =========================================================================
# Kabot-1 Mission: MPU6050 Logger (Flight-Ready with Heartbeat)
# =========================================================================

import time
from datetime import datetime
import os
import json
# import smbus or mpu6050 library as needed

FLIGHT_MODE = True

DATA_DIR = os.path.join("src", "logger", "data", "2_inflight")
DATA_FILE = os.path.join(DATA_DIR, "MPU6050.txt")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

HEARTBEAT_DIR = os.path.join("src", "logger", "data", "heartbeats")
HEARTBEAT_FILE = os.path.join(HEARTBEAT_DIR, "mpu_logger.json")

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

def write_heartbeat():
    os.makedirs(HEARTBEAT_DIR, exist_ok=True)
    try:
        with open(HEARTBEAT_FILE, "w") as f:
            json.dump({"last_heartbeat": datetime.now().isoformat()}, f)
    except:
        pass

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n")

    if not FLIGHT_MODE:
        print(f"MPU6050 Logger active. Logging to {DATA_FILE}.")
    main_loop()

def main_loop():
    try:
        while True:
            # Replace with actual sensor reads
            accel_x, accel_y, accel_z = 0.0, 0.0, 0.0
            gyro_x, gyro_y, gyro_z = 0.0, 0.0, 0.0

            timestamp = datetime.now().strftime("%H:%M:%S")
            data_line = f"{timestamp},{accel_x},{accel_y},{accel_z},{gyro_x},{gyro_y},{gyro_z}\n"
            with open(DATA_FILE, "a") as f:
                f.write(data_line)

            data_point = {
                "timestamp": timestamp,
                "accel_x": accel_x,
                "accel_y": accel_y,
                "accel_z": accel_z,
                "gyro_x": gyro_x,
                "gyro_y": gyro_y,
                "gyro_z": gyro_z
            }
            write_live_data(data_point)
            write_heartbeat()

            if not FLIGHT_MODE:
                print(f"\rLogged MPU6050 at {timestamp}", end="", flush=True)

            time.sleep(0.1)  # adjust sampling rate

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nMPU6050 logging terminated.")

if __name__ == "__main__":
    main()
