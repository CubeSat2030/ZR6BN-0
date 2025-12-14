# =========================================================================
# Kabot-1 Mission: Sound Logger & Buzzer Signaling (gpiozero)
# =========================================================================
# Purpose: Log sound amplitude (RMS + dB SPL) using ADS1115 and signal 
#          mission status using a high-level gpiozero buzzer interface.
# Hardware:
# 1. KY-037 Analog Out -> DFRobot ADC (ADS1115) A0
# 2. Buzzer -> Raspberry Pi GPIO 21
# =========================================================================

import time
import sys
import os
import json
import math
from datetime import datetime

# --- Third-Party Libraries ---
# Import gpiozero for high-level buzzer control (Requires: pip3 install gpiozero)
from gpiozero import Buzzer
# Import ADC libraries (Requires: pip3 install adafruit-circuitpython-ads1x15)
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
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
BUZZER_PIN = 21     # GPIO Pin for the passive/active buzzer
ADC_CHANNEL = ADS.P0 # ADC A0 pin connected to the microphone
ADC_GAIN = 1        # Sets the full-scale range to +/- 4.096V (ADS1115 default)

# Logging Setup
DATA_DIR = os.path.join("src", "logger", "data")
SOUND_DATA_FILE = os.path.join(DATA_DIR, "SOUND.csv")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

# Calibrated Reference Voltage (MUST be updated after running --calibrate)
# Placeholder value. Use the computed value after calibration.
V_REF = 1.0e-5 

# Logging Loop Parameters
SAMPLE_RATE = 100    # Samples per second (SPS)
WINDOW_SEC = 1       # RMS window length (seconds)
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
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    ads.gain = ADC_GAIN 
    chan = AnalogIn(ads, ADC_CHANNEL) 
except Exception as e:
    print(f"Error initializing I2C or ADC: {e}")
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
    # Uses generator expression (no intermediate list) for efficiency
    sum_of_squares = math.fsum(v**2 for v in samples)
    return math.sqrt(sum_of_squares / N)

# --- Calibration Mode ---

def calibrate(spl_ref=94.0):
    """Calibrate V_REF using a known SPL tone (e.g., 94 dB)."""
    
    print("\n--- Sound Sensor Calibration Mode ---")
    print(f"Targeting {N_SAMPLES} samples over {WINDOW_SEC} second(s).")
    print("!!! Start the known sound tone (e.g., 94 dB SPL) now !!!")
    
    samples = []
    start_time = time.monotonic()
    SAMPLE_PERIOD = 1.0 / SAMPLE_RATE
    
    for i in range(N_SAMPLES):
        read_start = time.monotonic()
        
        # --- Core ADC Read ---
        samples.append(chan.voltage)
        
        # --- Accurate Timing Loop ---
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
    
    buzz(duration_sec=0.2) # Single buzz to signal logger start
    main_loop()

def main_loop():
    """The main sampling and logging loop."""
    
    SAMPLE_PERIOD = 1.0 / SAMPLE_RATE

    try:
        while True:
            samples = []
            
            # Use monotonic time to ensure fixed window length
            for i in range(N_SAMPLES):
                read_start = time.monotonic()
                
                # --- Core ADC Read ---
                samples.append(chan.voltage)
                
                # --- Accurate Timing Loop ---
                read_end = time.monotonic()
                time_to_sleep = SAMPLE_PERIOD - (read_end - read_start)
                if time_to_sleep > 0:
                    time.sleep(time_to_sleep)
            
            # --- Data Processing ---
            rms = compute_rms(samples)
            
            # Compute dB SPL relative to V_REF
            if rms > 0 and V_REF > 0:
                db_spl = 20 * math.log10(rms / V_REF)
            else:
                db_spl = -math.inf 

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # --- Data Logging ---
            with open(SOUND_DATA_FILE, "a") as f:
                f.write(f"{timestamp},{rms:.9f},{db_spl:.2f}\n")

            data_point = {
                "timestamp": timestamp,
                "sound_rms": round(rms, 9),
                "sound_db": None if db_spl == -math.inf else round(db_spl, 2)
            }
            
            # --- System Health ---
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
        buzz(duration_sec=0.5) # Long buzz to signal shutdown
        buzzer.close() # Clean up gpiozero resources

# --- Entry Point ---

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--calibrate":
        calibrate()
    else:
        main()
