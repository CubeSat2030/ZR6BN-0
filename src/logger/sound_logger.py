import os
import time
import gpiozero # Correct library imported
import matplotlib.pyplot as plt
from datetime import datetime
import shutil

# --- Hardware Pins ---
# Keyes KY-038 D0 pin connected to GPIO14
SOUND_DETECTOR_PIN = 14
# Piezo Buzzer connected to GPIO21 (Standard BCM numbering assumed)
BUZZER_PIN = 21

# --- File Paths ---
DATA_FILE = "sound_data_D0.txt"
DATA_BACKUP_FILE = "sound_data_D0_backup.txt"
CHART_FILE = "sound_chart_D0.svg"
CHART_BACKUP_FILE = "sound_chart_D0_backup.svg"

# Global gpiozero objects
# These must be defined outside the function to persist their state
buzzer = None
sound_sensor = None


def log_sound_data():
    global buzzer, sound_sensor # Reference the global objects

    # --- Critical file existence and creation check ---
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp,sound_detected,is_buzzer_on\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return False

    # Backup data file
    if os.path.exists(DATA_FILE):
        shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)

    # --- GPIO Setup (using gpiozero objects) ---
    if buzzer is None or sound_sensor is None:
        try:
            # gpiozero uses BCM pin numbering by default
            buzzer = gpiozero.LED(BUZZER_PIN)
            # Use Button or DigitalInputDevice for the D0 sound sensor
            # Button is suitable for a simple digital signal
            sound_sensor = gpiozero.Button(SOUND_DETECTOR_PIN, pull_up=False) 
        except Exception as e:
            print(f"Error setting up gpiozero devices: {e}")
            return False

    # --- Test 1: Buzzer ON ---
    buzzer.on() # Turn the buzzer on
    print("Buzzer ON. Logging sound detection...")

    for _ in range(5):
        # sound_sensor.is_pressed returns True (1) if the circuit is closed (sound detected)
        # The D0 pin usually goes HIGH/LOW on sound; Button abstracts this.
        sound_detected = 1 if sound_sensor.is_pressed else 0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{sound_detected},1\n")
        time.sleep(1)

    buzzer.off() # Turn the buzzer off
    print("Buzzer OFF.")

    # --- Test 2: Ambient Sound (Buzzer OFF) ---
    print("Logging ambient sound detection...")

    for _ in range(5):
        sound_detected = 1 if sound_sensor.is_pressed else 0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{sound_detected},0\n")
        time.sleep(1)

    return True


def generate_chart():
    # Chart generation code remains the same as it correctly uses matplotlib
    dates, sound_detected_values, buzzer_states = [], [], []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            next(f)
            for line in f:
                try:
                    timestamp_str, sound_str, buzzer_str = line.strip().split(',')
                    dates.append(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"))
                    sound_detected_values.append(int(sound_str))
                    buzzer_states.append(int(buzzer_str))
                except (ValueError, IndexError):
                    continue

    if not dates:
        print("No data to chart.")
        return

    # Backup chart file
    if os.path.exists(CHART_FILE):
        shutil.copyfile(CHART_FILE, CHART_BACKUP_FILE) # Use copyfile instead of rename for safety/consistency

    # Use a modern matplotlib style
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.set_xlabel('Time')
    ax.set_ylabel('Sound Detected (1=Yes, 0=No)')
    ax.set_title('Sound Detection Test (D0 Pin)')
    # Use markers to show the discrete digital value
    ax.plot(dates, sound_detected_values, 'k.-', drawstyle='steps-mid', label='Sound Detected')

    # Indicate when the buzzer was ON
    buzzer_on_dates = [dates[i] for i, state in enumerate(buzzer_states) if state == 1]
    # Plot just above the 'detected' line for clarity
    buzzer_on_values = [1.1] * len(buzzer_on_dates)
    ax.plot(buzzer_on_dates, buzzer_on_values, 'ro', label='Buzzer ON', markersize=5)

    ax.set_yticks([0, 1])
    ax.set_ylim(-0.1, 1.2) # Set limits for better visibility
    plt.gcf().autofmt_xdate()
    ax.legend(loc='lower left')
    plt.tight_layout() # Adjust layout to prevent clipping
    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart saved to {CHART_FILE}.")


if __name__ == "__main__":
    try:
        # Initial call to setup the devices
        print("Starting sound logging application...")
        while True:
            if log_sound_data():
                generate_chart()
            time.sleep(1200) # Wait 20 minutes (1200 seconds)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    finally:
        # Cleanup pins on exit (optional but good practice)
        if buzzer:
            buzzer.close()
        if sound_sensor:
            sound_sensor.close()
