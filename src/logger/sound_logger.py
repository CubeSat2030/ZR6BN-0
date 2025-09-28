import os
import time
import gpiozero
from datetime import datetime
import shutil
import sys

# --- Hardware Pins (BCM Numbering) ---
SOUND_DETECTOR_PIN = 14
BUZZER_PIN = 21

# --- File Paths ---
# CHANGE 1: Define a directory for data files
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "sound_data_D0.txt")
DATA_BACKUP_FILE = os.path.join(DATA_DIR, "sound_data_D0_backup.txt")

# --- Configuration ---
# Define your desired buzzer frequency (e.g., 440 Hz for an A note)
BUZZER_FREQUENCY_HZ = 440

# --- Global gpiozero objects ---
buzzer = None
sound_sensor = None

def log_sound_data():
    """Initializes hardware, performs sound tests, and logs data robustly."""
    global buzzer, sound_sensor

    # CHANGE 2: Ensure the data directory exists before doing anything else
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print(f"Created data directory: {DATA_DIR}")
    except Exception as e:
        print(f"FATAL: Could not create data directory: {e}", file=sys.stderr)
        return False

    # --- Critical file existence and creation check ---
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                # Adding system_uptime_s for reliable time measurement
                f.write("timestamp_utc,system_uptime_s,sound_detected,is_buzzer_on\n")
        except Exception as e:
            print(f"Error creating file: {e}", file=sys.stderr)
            return False

    # --- Backup data file before adding new data ---
    try:
        if os.path.exists(DATA_FILE):
            shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)
    except Exception as e:
        print(f"Warning: Could not create data backup: {e}", file=sys.stderr)

    # --- GPIO Setup (Only runs once) ---
    if buzzer is None or sound_sensor is None:
        try:
            # Instantiate buzzer as PWMOutputDevice to control frequency
            buzzer = gpiozero.PWMOutputDevice(BUZZER_PIN, frequency=BUZZER_FREQUENCY_HZ)
            # Use Button for the digital sound sensor D0 pin
            sound_sensor = gpiozero.Button(SOUND_DETECTOR_PIN, pull_up=False)
        except Exception as e:
            print(f"FATAL: Error setting up gpiozero devices: {e}", file=sys.stderr)
            if buzzer: buzzer.close()
            if sound_sensor: sound_sensor.close()
            return False

    # --- Test 1: Buzzer ON (5 seconds of logging) ---
    print("Starting Test 1: Buzzer ON")
    if isinstance(buzzer, gpiozero.PWMOutputDevice):
        buzzer.frequency = BUZZER_FREQUENCY_HZ
    buzzer.on()  # Turn the buzzer on

    for _ in range(5):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        system_uptime = time.monotonic()
        sound_detected = 1 if sound_sensor.is_pressed else 0

        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{system_uptime:.2f},{sound_detected},1\n")
        time.sleep(1)

    buzzer.off()  # Turn the buzzer off
    print("Finished Test 1.")

    # A brief pause between tests
    time.sleep(1)

    # --- Test 2: Ambient Sound (Buzzer OFF - 5 seconds of logging) ---
    print("Starting Test 2: Ambient Sound")
    for _ in range(5):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        system_uptime = time.monotonic()
        sound_detected = 1 if sound_sensor.is_pressed else 0

        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{system_uptime:.2f},{sound_detected},0\n")
        time.sleep(1)
    print("Finished Test 2.")
    
    return True

if __name__ == "__main__":
    print(f"Starting HAB Payload Logger...")
    print(f"Buzzer frequency set to: {BUZZER_FREQUENCY_HZ} Hz")

    try:
        # Initial call to set up devices and log the first data point
        if not log_sound_data():
            print("Initial hardware setup failed. Exiting.")
            sys.exit(1)

        while True:
            print(f"Cycle finished. Waiting 20 minutes (1200 seconds)...")
            time.sleep(1200)
            
            if not log_sound_data():
                print("Logging cycle failed. Retrying after 20 minutes.")

    except KeyboardInterrupt:
        print("\nApplication stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"\nFATAL UNHANDLED EXCEPTION: {e}", file=sys.stderr)
    finally:
        # Clean up GPIO pins to prevent issues on next boot
        print("Cleaning up GPIO pins...")
        if buzzer:
            buzzer.close()
        if sound_sensor:
            sound_sensor.close()
        print("Application terminated.")


