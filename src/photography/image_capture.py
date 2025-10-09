# =========================================================================
# Kabot-1 Mission: Image Capture Logger (Flight-Ready with Heartbeat)
# =========================================================================
# Captures timestamped images from Pi Camera (Picamera2).
# Outputs to mission data directory, updates central JSON, and emits heartbeat.
# =========================================================================

import os
import time
import json
from datetime import datetime
from heartbeat import write_heartbeat
from picamera2 import Picamera2

# --- Configuration ---
FLIGHT_MODE = True  # Silence console output during flight

DATA_DIR = os.path.join("src", "logger", "data")
IMG_DIR = os.path.join(DATA_DIR, "images")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

CAPTURE_INTERVAL = 30  # seconds between captures

# --- Camera Setup ---
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 720)})
picam2.configure(config)
picam2.start()

# --- Utility Functions ---

def write_live_data(data):
    """Update centralized JSON file for dashboard."""
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

def capture_image():
    """Capture a single image and save with timestamped filename."""
    os.makedirs(IMG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(IMG_DIR, f"img_{timestamp}.jpg")
    picam2.capture_file(filename)
    return filename, timestamp

# --- Main Loop ---

def main():
    if not FLIGHT_MODE:
        print(f"Image Capture Logger active. Saving to {IMG_DIR} every {CAPTURE_INTERVAL}s.")

    try:
        while True:
            filename, timestamp = capture_image()

            # Update JSON with last image metadata
            data_point = {
                "last_image_timestamp": timestamp,
                "last_image_file": os.path.basename(filename)
            }
            write_live_data(data_point)

            # Heartbeat
            write_heartbeat("image_capture.json")

            if not FLIGHT_MODE:
                print(f"[{timestamp}] Captured {filename}")

            time.sleep(CAPTURE_INTERVAL)

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nImage capture terminated.")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()
