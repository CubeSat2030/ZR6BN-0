import os
import time
import shutil
from datetime import datetime

# Import the correct library: gpiozero
from gpiozero import Button, LED
from signal import pause # Not used, but harmless

# --- Hardware Pins ---
# Keyes KY-038 D0 pin connected to GPIO14. We use Button for digital input.
SOUND_DETECTOR_PIN = 14
# Piezo Buzzer connected to GPIO4. We use LED (a simple output device) for the buzzer.
BUZZER_PIN = 21

# --- File Paths ---
DATA_FILE = "sound_data_D0.txt"
DATA_BACKUP_FILE = "sound_data_D0_backup.txt"
# Chart file paths removed as charting is no longer supported without NumPy/Matplotlib.

# --- Device Initialization ---
# Initialize the GPIO devices ONCE outside the loop.
# gpiozero handles setup and automatic cleanup upon script exit.
sound_detector = None
buzzer = None
try:
    # Button is used for digital input (D0 pin). pull_up=False often matches active-low sensors.
    sound_detector = Button(SOUND_DETECTOR_PIN, pull_up=False)
    buzzer = LED(BUZZER_PIN) # LED acts as a simple digital output for the buzzer
    print("GPIO devices initialized successfully.")
except Exception as e:
    # This block handles potential errors if the script is run off-platform or pins are busy.
    print(f"Error initializing GPIO devices. The script may run but skip GPIO operations: {e}")

def initialize_data_file():
    """Checks for and initializes the data file."""
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,sound_detected,is_buzzer_on\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return False
    return True

def log_sound_data():
    """Runs the logging sequence, controlling the buzzer and reading the sound sensor."""

    # We must check if the devices were initialized successfully before using them.
    if sound_detector is None or buzzer is None:
        print("Skipping sound logging: GPIO devices not initialized.")
        return True # Return True if the process completed its steps

    # Backup data file
    if os.path.exists(DATA_FILE):
        try:
            shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)
        except Exception as e:
            print(f"Warning: Could not create data file backup: {e}")

    # --- Test 1: Buzzer ON ---
    buzzer.on()
    print("Buzzer ON. Logging sound detection...")

    for i in range(5):
        try:
            # .is_pressed returns True (1) or False (0). Convert to int.
            sound_detected = int(sound_detector.is_pressed)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(DATA_FILE, "a") as f:
                f.write(f"{timestamp},{sound_detected},1\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error during Test 1 logging at iteration {i}: {e}")
            break

    buzzer.off()
    print("Buzzer OFF.")

    # --- Test 2: Ambient Sound (Buzzer OFF) ---
    print("Logging ambient sound detection...")

    for i in range(5):
        try:
            # .is_pressed returns True (1) or False (0). Convert to int.
            sound_detected = int(sound_detector.is_pressed)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(DATA_FILE, "a") as f:
                f.write(f"{timestamp},{sound_detected},0\n")
            time.sleep(1)
        except Exception as e:
            print(f"Error during Test 2 logging at iteration {i}: {e}")
            break

    return True

# The generate_chart function has been removed because it relies on Matplotlib, which in turn
# relies heavily on NumPy.

if __name__ == "__main__":
    if not initialize_data_file():
        exit()

    try:
        while True:
            # We now only call log_sound_data()
            if log_sound_data():
                # Data is logged successfully, but chart generation is skipped.
                pass
            print(f"Waiting for 1200 seconds before next cycle...")
            time.sleep(1200)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")

    except Exception as e:
        print(f"\nAn unhandled error occurred: {e}")
    
    # Cleanup ensures the buzzer is off before the script finally exits.
    finally:
        if buzzer:
            buzzer.off()
            print("Buzzer turned off and resources released.")

