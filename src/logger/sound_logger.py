import os
import time
import gpiozero
from datetime import datetime
import shutil
import sys 
import time

# --- Hardware Pins (BCM Numbering) ---
SOUND_DETECTOR_PIN = 14
BUZZER_PIN = 21

# --- File Paths ---
DATA_FILE = "sound_data_D0.txt"
DATA_BACKUP_FILE = "sound_data_D0_backup.txt"

# Global gpiozero objects
# CHANGE 1: Use PWMOutputDevice for a buzzer to control frequency
buzzer = None 
sound_sensor = None

# --- NEW CONFIGURATION ---
# Define your desired buzzer frequency (e.g., 440 Hz for an A note)
BUZZER_FREQUENCY_HZ = 880 # Example: A higher frequency tone

# --- NEW FUNCTION FOR TONE ---
def play_tone(duration_s, frequency_hz):
    """Plays the buzzer tone for a specified duration and frequency."""
    global buzzer
    if buzzer is not None:
        # Check if the buzzer is a PWMOutputDevice
        if isinstance(buzzer, gpiozero.PWMOutputDevice):
            # Set the frequency and start the PWM with 50% duty cycle (on())
            buzzer.frequency = frequency_hz 
            buzzer.on() # Starts PWM at its current frequency/value
            time.sleep(duration_s)
            buzzer.off()
        else:
            # Fallback for simple LED (just turns it on/off)
            buzzer.on()
            time.sleep(duration_s)
            buzzer.off()


def log_sound_data():
    """Initializes hardware, performs sound tests, and logs data robustly."""
    global buzzer, sound_sensor 

    # --- Critical file existence and creation check ---
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found. Creating {DATA_FILE}...")
        try:
            with open(DATA_FILE, "w") as f:
                # Adding system_uptime_s for reliable time measurement during flight
                f.write("timestamp_utc,system_uptime_s,sound_detected,is_buzzer_on\n")
        except Exception as e:
            print(f"Error creating file: {e}", file=sys.stderr)
            return False

    # Backup data file before adding new data
    try:
        if os.path.exists(DATA_FILE):
            shutil.copyfile(DATA_FILE, DATA_BACKUP_FILE)
    except Exception as e:
        print(f"Warning: Could not create data backup: {e}", file=sys.stderr)

    # --- GPIO Setup (Only runs once) ---
    if buzzer is None or sound_sensor is None:
        try:
            # gpiozero uses BCM pin numbering by default
            # CHANGE 2: Instantiate as PWMOutputDevice
            buzzer = gpiozero.PWMOutputDevice(BUZZER_PIN, frequency=BUZZER_FREQUENCY_HZ) 
            # Use Button for the digital sound sensor D0 pin
            sound_sensor = gpiozero.Button(SOUND_DETECTOR_PIN, pull_up=False) 
        except Exception as e:
            print(f"FATAL: Error setting up gpiozero devices: {e}", file=sys.stderr)
            if buzzer: buzzer.close()
            if sound_sensor: sound_sensor.close()
            return False

    # Get the timestamps before the logging sequence starts
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    system_uptime = time.monotonic() 
    
    # --- Test 1: Buzzer ON (5 seconds of logging) ---
    # CHANGE 3: Use the new play_tone function for a specific frequency
    # We will log the state for the duration of the tone
    
    # Calculate logging steps for the 5-second duration
    log_interval = 1 
    num_steps = 5
    
    # Start the tone and the logging loop
    if isinstance(buzzer, gpiozero.PWMOutputDevice):
        buzzer.frequency = BUZZER_FREQUENCY_HZ
    buzzer.on() # Turn the buzzer on (with the set frequency)
    
    for _ in range(num_steps):
        sound_detected = 1 if sound_sensor.is_pressed else 0
        
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{system_uptime:.2f},{sound_detected},1\n")
        time.sleep(log_interval)

    buzzer.off() # Turn the buzzer off

    # --- Test 2: Ambient Sound (Buzzer OFF - 5 seconds of logging) ---
    for _ in range(5):
        sound_detected = 1 if sound_sensor.is_pressed else 0
        
        with open(DATA_FILE, "a") as f:
            f.write(f"{timestamp},{system_uptime:.2f},{sound_detected},0\n")
        time.sleep(1)

    return True


# ... (rest of the code remains the same) ...

if __name__ == "__main__":
    print(f"Starting HAB Payload Logger (Matplotlib disabled)...")
    print(f"Buzzer frequency set to: {BUZZER_FREQUENCY_HZ} Hz") # Print the new frequency
    
    try:
        # Initial call to set up devices and log the first data point
        if not log_sound_data():
             print("Initial hardware setup failed. Exiting.")
             sys.exit(1)

        while True:
            if log_sound_data():
                pass # The data is logged successfully
                
            print(f"Cycle finished. Waiting 20 minutes (1200 seconds)...")
            time.sleep(5) 
            
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
