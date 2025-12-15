# =========================================================================
# Kabot-1 Mission: Sound Logger & Buzzer Signaling (I2C Channel Fix)
# =========================================================================
# Purpose: Log sound amplitude (RMS + dB SPL) using ADS1115 and signal 
#          mission status using a high-level gpiozero buzzer interface.
# Fix: Corrects the 'no attribute P0/A0' error by importing P0 from the 
#      ADS1015 submodule, which hosts the shared channel constants.
# =========================================================================

import time
import sys
import os
import json
import math
from datetime import datetime

# --- Third-Party Libraries ---
from gpiozero import Buzzer
import board 
# Import the ADS1115 class
import adafruit_ads1x15.ads1115 as ADS
# Import the ADS1015 module to access the shared P0 channel constant
import adafruit_ads1x15.ads1015 as ADS_CHANNEL_CONSTANTS 
from adafruit_ads1x15.analog_in import AnalogIn

# Assume write_heartbeat is available in current environment
try:
    from heartbeat import write_heartbeat 
except ImportError:
    def write_heartbeat(filename):
        pass

# --- Configuration & Constants ---
FLIGHT_MODE = True  # Set to True for minimal console output

# Hardware Pinouts
BUZZER_PIN = 21     
ADC_GAIN = 1        

# Logging Setup
DATA_DIR = os.path.join("src", "logger", "data")
SOUND_DATA_FILE = os.path.join(DATA_DIR, "SOUND.csv")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

# Calibrated Reference Voltage 
V_REF = 1.0e-5 

# Logging Loop Parameters
SAMPLE_RATE = 100    
WINDOW_SEC = 1       
N_SAMPLES = SAMPLE_RATE * WINDOW_SEC

# --- Initialize Hardware ---
# 1. gpiozero Buzzer
try:
    buzzer = Buzzer(BUZZER_PIN)
except Exception as e:
    print(f"Error initializing Buzzer on GPIO {BUZZER_PIN}: {e}")
    sys.exit(1)

# 2. I2C and ADC
try:
    i2c = board.I2C() 
    ads = ADS.ADS1115(i2c)
    ads.gain = ADC_GAIN 
    
    # CORRECT FIX: Use the P0 constant from the imported ADS_CHANNEL_CONSTANTS module
    chan = AnalogIn(ads, ADS_CHANNEL_CONSTANTS.P0) 
    
except Exception as e:
    print(f"Error initializing I2C or ADC: {e}")
    print("Ensure I2C is enabled and that all adafruit-ads1x15 dependencies are installed.")
    sys.exit(1)
    
# --- Utility Functions ---

def buzz(duration_sec=0.1, delay_sec=0.1, repeats=1):
    """Activates the buzzer for signaling using gpiozero."""
    for _ in range(repeats):
        buzzer.on()
        time.sleep(duration_sec)
        buzzer.off()
        if repeats > 1:
            time.sleep(delay_sec)

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

def compute_rms(samples):
    """Compute RMS from a list of voltage samples using efficient generator."""
    N = len(samples)
    if N == 0:
        return 0.0
    sum_of_squares = math.fsum(v**2 for v in samples)
    return math.sqrt(sum_of_squares / N)

# --- Calibration Mode ---

def calibrate(spl_ref=94.0):
    """Calibrate V_REF using a known SPL tone (e.g., 94 dB)."""
    
    print("\n--- Sound Sensor Calibration Mode ---")
    print(f"Targeting {N_SAMPLES} samples over {WINDOW_SEC} second(s).")
    print("!!! Start the known sound tone (e.g., 94 dB SPL) now !!!")
    
    samples = []
    SAMPLE_PERIOD = 1.0 / SAMPLE_RATE
    
    for i in range(N_SAMPLES):
        read_start = time.monotonic()
        samples.append(chan.voltage)
        read_end = time.monotonic()
        time_to_sleep = SAMPLE_PERIOD - (read_end - read_start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
    
    rms = compute_rms(samples)
    
    if rms > 0:
        v_ref_computed = rms / (10**(spl_ref / 20))
    else:
        v_ref_computed = 0.0

    print(f"\nCalibration Results ({datetime.now().isoformat()}):")
    print(f"  Measured RMS Voltage: {rms:.9f} V")
    print(f"  Calibration SPL: {spl_ref:.2f} dB")
    print(f"  Computed V_REF (for 0 dB SPL): {v_ref_computed:.9e} V")
    print("\n!!! Update the 'V_REF' variable in the script with this value. !!!")
    buzz(duration_sec=0.05, repeats=3)


# --- Logging Mode ---

def main():
    """Setup and entry point for the continuous logging mode."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(SOUND_DATA_FILE):
        with open(SOUND_DATA_FILE, "w") as f:
            f.write("timestamp,rms_voltage(V),sound_level(dB SPL)\n")

    if not FLIGHT_MODE:
        print(f"Sound Logger active. Logging to {SOUND_DATA_FILE}.")
        print(f"V_REF currently set to: {V_REF:.9e} V")
    
    buzz(duration_sec=0.2) 
    main_loop()

def main_loop():
    """The main sampling and logging loop."""
    
    SAMPLE_PERIOD = 1.0 / SAMPLE_RATE

    try:
        while True:
            samples = []
            
            for i in range(N_SAMPLES):
                read_start = time.monotonic()
                samples.append(chan.voltage)
                read_end = time.monotonic()
                time_to_sleep = SAMPLE_PERIOD - (read_end - read_start)
                if time_to_sleep > 0:
                    time.sleep(time_to_sleep)
            
            rms = compute_rms(samples)
            
            if rms > 0 and V_REF > 0:
                db_spl = 20 * math.log10(rms / V_REF)
            else:
                db_spl = -math.inf 

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(SOUND_DATA_FILE, "a") as f:
                f.write(f"{timestamp},{rms:.9f},{db_spl:.2f}\n")

            data_point = {
                "timestamp": timestamp,
                "sound_rms": round(rms, 9),
                "sound_db": None if db_spl == -math.inf else round(db_spl, 2)
            }
            
            write_live_data(data_point)
            write_heartbeat("sound_logger.json")

            if not FLIGHT_MODE:
                print(f"\rLogged RMS: {rms:.9f} V | {db_spl:.2f} dB SPL at {timestamp}", end="", flush=True)

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nSound logging terminated by user.")
    except Exception as e:
        if not FLIGHT_MODE:
            print(f"\nAn error occurred in main loop: {e}")
    finally:
        buzz(duration_sec=0.5) 
        buzzer.close() 

# --- Entry Point ---

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--calibrate":
        calibrate()
    else:
        main()
