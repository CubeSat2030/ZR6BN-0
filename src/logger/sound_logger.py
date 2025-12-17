
# =========================================================================
# Kabot-1 Mission: Sound Logger & Buzzer Signaling (3-Second Combined Cycle)
# =========================================================================
# Purpose: Log sound amplitude (RMS + dB SPL) during a 3-second signaling beep,
#          then sleep for the remainder of the minute.
# Cycle: [BEEP + CAPTURE (3s)] -> [SILENCE/SLEEP (57s)]
# Total Cycle Time: 60.0 seconds
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

# NEW CONFIG: The time between the start of two consecutive captures
CYCLE_INTERVAL_SEC = 60.0 # 1 minute
CAPTURE_DURATION_SEC = 3.0 # CAPTURE NOW LASTS 3.0 SECONDS
BUZZER_DURATION_SEC = CAPTURE_DURATION_SEC # Buzzer is ON for the entire capture duration

# Hardware Pinouts
BUZZER_PIN = 21     
ADC_GAIN = 1        

# Logging Setup
DATA_DIR = os.path.join("src", "logger", "data")
SOUND_DATA_FILE = os.path.join(DATA_DIR, "SOUND.txt")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

# Calibrated Reference Voltage 
V_REF = 1.0e-5 

# Logging Loop Parameters
SAMPLE_RATE = 100    
# Calculate N_SAMPLES based on the new 3.0s duration
N_SAMPLES = int(SAMPLE_RATE * CAPTURE_DURATION_SEC) 

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
    chan = AnalogIn(ads, 0) # Guaranteed Fix: Use channel index 0 (for A0)
    
except Exception as e:
    print(f"Error initializing I2C or ADC: {e}")
    sys.exit(1)
    
# --- Utility Functions ---

# NOTE: The buzz function is simplified here as we will control ON/OFF 
# manually inside the main loop for the precise 3.0s duration.
def buzz_on():
    """Activates the buzzer."""
    buzzer.on()

def buzz_off():
    """Deactivates the buzzer."""
    buzzer.off()
    
# ... (write_live_data and compute_rms functions remain unchanged) ...
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

def compute_rms(samples):
    N = len(samples)
    if N == 0:
        return 0.0
    sum_of_squares = math.fsum(v**2 for v in samples)
    return math.sqrt(sum_of_squares / N)

# --- Calibration Mode (Updated to use 3.0s capture) ---
def calibrate(spl_ref=94.0):
    print("\n--- Sound Sensor Calibration Mode ---")
    print(f"Targeting {N_SAMPLES} samples over {CAPTURE_DURATION_SEC} second(s).")
    print("!!! Start the known sound tone now !!!")
    
    samples = []
    SAMPLE_PERIOD = 1.0 / SAMPLE_RATE
    
    # Manually turn buzzer on for calibration signal
    buzz_on() 
    
    for i in range(N_SAMPLES):
        read_start = time.monotonic()
        samples.append(chan.voltage)
        read_end = time.monotonic()
        time_to_sleep = SAMPLE_PERIOD - (read_end - read_start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
            
    buzz_off() # Turn buzzer off after capture

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
    # Use simple buzz_on/off for final signal
    buzzer.on()
    time.sleep(0.05)
    buzzer.off()
    time.sleep(0.05)
    buzzer.on()
    time.sleep(0.05)
    buzzer.off()


# --- Logging Mode (Restructured for 3s combined event) ---

def main():
    """Setup and entry point for the 1-minute cyclical logging mode."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(SOUND_DATA_FILE):
        with open(SOUND_DATA_FILE, "w") as f:
            f.write("timestamp,rms_voltage(V),sound_level(dB SPL)\n") 

    if not FLIGHT_MODE:
        print(f"Cyclical Sound Logger active. Interval: {CYCLE_INTERVAL_SEC}s ({CAPTURE_DURATION_SEC}s combined capture).")
    
    # Use old buzz function for clean start signal
    buzzer.on()
    time.sleep(0.2)
    buzzer.off() 
    
    main_loop()

def main_loop():
    """The main 60-second sampling and sleeping loop."""
    
    SAMPLE_PERIOD = 1.0 / SAMPLE_RATE
    next_cycle_start_time = time.monotonic()

    try:
        while True:
            # 1. WAIT FOR NEXT CYCLE START
            time_to_wait = next_cycle_start_time - time.monotonic()
            if time_to_wait > 0:
                 time.sleep(time_to_wait)
                 
            # 2. START OF CYCLE (BEEP & CAPTURE PHASE)
            cycle_start_time = time.monotonic()
            
            # --- START BEEP AND CAPTURE (3.0s) ---
            buzz_on() # Buzzer ON
            
            samples = []
            
            # Data Sampling for the full CAPTURE_DURATION_SEC (3.0 seconds)
            for i in range(N_SAMPLES):
                read_start = time.monotonic()
                samples.append(chan.voltage)
                read_end = time.monotonic()
                time_to_sleep = SAMPLE_PERIOD - (read_end - read_start)
                if time_to_sleep > 0:
                    time.sleep(time_to_sleep)
            
            buzz_off() # Buzzer OFF - End of the 3.0s event
            
            # 3. PROCESSING & LOGGING (The short silent gap after capture)
            rms = compute_rms(samples)
            
            if rms > 0 and V_REF > 0:
                db_spl = 20 * math.log10(rms / V_REF)
            else:
                db_spl = -math.inf 

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Logging to file
            with open(SOUND_DATA_FILE, "a") as f:
                f.write(f"{timestamp},{rms:.9f},{db_spl:.2f}\n")
                
            data_point = {
                "timestamp": timestamp,
                "sound_rms": round(rms, 9),
                "sound_db": None if db_spl == -math.inf else round(db_spl, 2)
            }
            
            write_live_data(data_point)
            write_heartbeat("sound_logger.json")

            # 4. ADVANCE NEXT CYCLE START TIME
            # Ensures the next cycle starts exactly 60 seconds after this one started.
            next_cycle_start_time = cycle_start_time + CYCLE_INTERVAL_SEC
            
            # --- CONSOLE OUTPUT ---
            if not FLIGHT_MODE:
                print(f"\rLogged {db_spl:.2f} dB SPL at {timestamp} over 3s. Sleeping for {CYCLE_INTERVAL_SEC - CAPTURE_DURATION_SEC:.1f}s...", end="", flush=True)

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nSound logging terminated by user.")
    except Exception as e:
        if not FLIGHT_MODE:
            print(f"\nAn error occurred in main loop: {e}")
    finally:
        # Long buzz to signal shutdown
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        buzzer.close() 

# --- Entry Point ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--calibrate":
        calibrate()
    else:
        main()
