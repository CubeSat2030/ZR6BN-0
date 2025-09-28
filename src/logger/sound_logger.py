import os
import time
import gpiozero
import matplotlib.pyplot as plt
from datetime import datetime
import shutil
import sys # Import sys for better exception handling

# --- CRITICAL HAB MODE FLAG (MUST BE SET BEFORE LAUNCH) ---
# Set to 'False' for flight to save power and memory (RECOMMENDED).
# Set to 'True' ONLY for ground testing or post-flight analysis.
RUN_CHART_GENERATION_IN_FLIGHT = False

# --- Hardware Pins (BCM Numbering) ---
SOUND_DETECTOR_PIN = 14
BUZZER_PIN = 21

# --- File Paths ---
DATA_FILE = "sound_data_D0.txt"
DATA_BACKUP_FILE = "sound_data_D0_backup.txt"
CHART_FILE = "sound_chart_D0.svg"
CHART_BACKUP_FILE = "sound_chart_D0_backup.svg"

# Global gpiozero objects
buzzer = None
sound_sensor = None


def log_sound_data():
    """Initializes hardware, performs sound tests, and logs data robustly."""
    global buzzer, sound_sensor # Reference the global objects

    # --- Critical file existence and creation check ---
    # File header is critical for generate_chart()
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                f.write("timestamp_utc,system_uptime_s,sound_detected,is_buzzer_on\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            return False

    # Backup data file before adding new data
    try:
        if os.path.exists(DATA_FILE):
            shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)
    except Exception as e:
        print(f"Warning: Could not create data backup: {e}")

    # --- GPIO Setup (Only runs once) ---
    if buzzer is None or sound_sensor is None:
        try:
            # gpiozero uses BCM pin numbering by default
            buzzer = gpiozero.LED(BUZZER_PIN)
            # Use Button for the digital sound sensor D0 pin
            sound_sensor = gpiozero.Button(SOUND_DETECTOR_PIN, pull_up=False) 
        except Exception as e:
            print(f"FATAL: Error setting up gpiozero devices: {e}")
            # Ensure any partial setup is cleaned up
            if buzzer: buzzer.close()
            if sound_sensor: sound_sensor.close()
            return False

    # Get two crucial timestamps:
    # 1. timestamp_utc: Wall-clock time (may drift without network sync)
    # 2. system_uptime_s: Monotonic time (reliable for interval timing)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    system_uptime = time.monotonic() 
    
    # --- Test 1: Buzzer ON ---
    buzzer.on() 
    # In a real payload, minimize printing to console to save minor power/CPU
    # print("Buzzer ON. Logging sound detection...") 

    for _ in range(5):
        # sound_sensor.is_pressed returns True (1) or False (0)
        sound_detected = 1 if sound_sensor.is_pressed else 0
        
        # Log data immediately for robust data saving
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{system_uptime:.2f},{sound_detected},1\n")
        time.sleep(1)

    buzzer.off() 
    # print("Buzzer OFF.")

    # --- Test 2: Ambient Sound (Buzzer OFF) ---
    # print("Logging ambient sound detection...")

    for _ in range(5):
        sound_detected = 1 if sound_sensor.is_pressed else 0
        
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{system_uptime:.2f},{sound_detected},0\n")
        time.sleep(1)

    return True


def generate_chart():
    """Generates a chart using Matplotlib (Heavy, skip during flight)."""
    
    # Check for memory and environment (optional, but a good practice on limited RAM)
    # print("Warning: Matplotlib is highly memory-intensive (512MB RAM on Pi Zero W).")
    
    dates, sound_detected_values, buzzer_states = [], [], []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            next(f) # Skip header
            for line in f:
                try:
                    # Expecting: timestamp_utc,system_uptime_s,sound_detected,is_buzzer_on
                    parts = line.strip().split(',')
                    timestamp_str = parts[0]
                    # We are using column index 2 and 3 for the data
                    sound_str = parts[2] 
                    buzzer_str = parts[3]
                    
                    dates.append(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"))
                    sound_detected_values.append(int(sound_str))
                    buzzer_states.append(int(buzzer_str))
                except (ValueError, IndexError):
                    # Robustly skip bad lines
                    continue

    if not dates:
        print("No valid data to chart.")
        return

    # Backup chart file before generating new one
    try:
        if os.path.exists(CHART_FILE):
            shutil.copyfile(CHART_FILE, CHART_BACKUP_FILE)
    except Exception as e:
        print(f"Warning: Could not backup chart file: {e}")

    # Use a modern matplotlib style
    plt.style.use('ggplot')
    # Use a small figure size to conserve memory/CPU during chart generation
    fig, ax = plt.subplots(figsize=(8, 5)) 

    ax.set_xlabel('Time (UTC)')
    ax.set_ylabel('Sound Detected (1=Yes, 0=No)')
    ax.set_title('Sound Detection Test (D0 Pin)')
    
    # Plot the digital sound data
    ax.plot(dates, sound_detected_values, 'k.-', drawstyle='steps-mid', label='Sound Detected')

    # Indicate when the buzzer was ON
    buzzer_on_dates = [dates[i] for i, state in enumerate(buzzer_states) if state == 1]
    buzzer_on_values = [1.1] * len(buzzer_on_dates)
    ax.plot(buzzer_on_dates, buzzer_on_values, 'ro', label='Buzzer ON', markersize=5)

    ax.set_yticks([0, 1])
    ax.set_ylim(-0.1, 1.2)
    plt.gcf().autofmt_xdate()
    ax.legend(loc='lower left')
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close(fig)
    print(f"Chart saved to {CHART_FILE}.")


if __name__ == "__main__":
    print(f"Starting sound logging application on RPi Zero W (512MB RAM)...")
    print(f"Chart generation set to: {RUN_CHART_GENERATION_IN_FLIGHT}")
    
    # Optional: Perform initial setup of devices outside the loop for immediate failure check
    log_sound_data() 
    
    try:
        while True:
            # Only proceed if hardware setup was successful
            if log_sound_data():
                # Conditional execution of the heavy charting function
                if RUN_CHART_GENERATION_IN_FLIGHT:
                    generate_chart()
                
            # Log successful cycle and wait
            print(f"Cycle finished. Waiting 20 minutes...")
            time.sleep(1200) # Wait 20 minutes (1200 seconds)
            
    except KeyboardInterrupt:
        print("\nApplication stopped by user (KeyboardInterrupt).")
    except Exception as e:
        # Log any unexpected exceptions before exiting
        print(f"\nFATAL UNHANDLED EXCEPTION: {e}", file=sys.stderr)
    finally:
        # Clean up GPIO pins to prevent issues on next boot
        print("Cleaning up GPIO pins...")
        if buzzer:
            buzzer.close()
        if sound_sensor:
            sound_sensor.close()
        print("Application terminated.")
