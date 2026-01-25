# =========================================================================
# Kabot-1 Mission: Sound Logger & Buzzer Signaling (Robust GPIO Version)
# =========================================================================
# Purpose: Log sound amplitude during a 3s beep, then sleep for 57s.
# Patch: Added retry logic for GPIO initialization to prevent "Pin Busy" crashes.
# =========================================================================

import time
import sys
import os
import json
import math
from datetime import datetime

# --- Third-Party Libraries ---
try:
    from gpiozero import Buzzer
    import board 
    import adafruit_ads1x15.ads1115 as ADS 
    from adafruit_ads1x15.analog_in import AnalogIn
except ImportError as e:
    print(f"CRITICAL: Missing libraries: {e}")
    sys.exit(1)

try:
    from heartbeat import write_heartbeat 
except ImportError:
    def write_heartbeat(filename): pass

# --- Configuration ---
FLIGHT_MODE = True  
CYCLE_INTERVAL_SEC = 60.0 
CAPTURE_DURATION_SEC = 3.0 
BUZZER_PIN = 4     
ADC_GAIN = 1        
DATA_DIR = os.path.join("src", "logger", "data", "3_postflight")
SOUND_DATA_FILE = os.path.join(DATA_DIR, "sound_logger.txt")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")
V_REF = 1.0e-5 
SAMPLE_RATE = 100    
N_SAMPLES = int(SAMPLE_RATE * CAPTURE_DURATION_SEC) 

# --- ROBUST HARDWARE INITIALIZATION ---

def get_buzzer_safe(retries=5, delay=1):
    """Attempt to grab the buzzer pin, retrying if the web server is currently using it."""
    for i in range(retries):
        try:
            bz = Buzzer(BUZZER_PIN)
            return bz
        except Exception as e:
            if not FLIGHT_MODE:
                print(f"GPIO 4 Busy (Attempt {i+1}/{retries}). Waiting...")
            time.sleep(delay)
    raise Exception(f"Could not initialize Buzzer on GPIO {BUZZER_PIN} after {retries} attempts. Pin is busy.")

# Initialize ADC
try:
    i2c = board.I2C() 
    ads = ADS.ADS1115(i2c)
    ads.gain = ADC_GAIN 
    chan = AnalogIn(ads, 0)
except Exception as e:
    print(f"CRITICAL: ADC/I2C Init Failed: {e}")
    sys.exit(1)

# --- Utility Functions ---

def write_live_data(data):
    full_data = {}
    if os.path.exists(LIVE_DATA_FILE):
        try:
            with open(LIVE_DATA_FILE, 'r') as f:
                full_data = json.load(f)
        except: pass 
    full_data.update(data)
    try:
        with open(LIVE_DATA_FILE, 'w') as f:
            json.dump(full_data, f, indent=4)
    except: pass 

def compute_rms(samples):
    N = len(samples)
    if N == 0: return 0.0
    return math.sqrt(math.fsum(v**2 for v in samples) / N)

# --- Logging Mode ---

def main_loop():
    SAMPLE_PERIOD = 1.0 / SAMPLE_RATE
    next_cycle_start_time = time.monotonic()

    try:
        while True:
            time_to_wait = next_cycle_start_time - time.monotonic()
            if time_to_wait > 0:
                 time.sleep(time_to_wait)
                 
            cycle_start_time = time.monotonic()
            
            # --- START BEEP AND CAPTURE (3.0s) ---
            # We open the buzzer right before we need it and close it immediately after
            bz = get_buzzer_safe()
            try:
                bz.on()
                samples = []
                for i in range(N_SAMPLES):
                    read_start = time.monotonic()
                    samples.append(chan.voltage)
                    read_end = time.monotonic()
                    time_to_sleep = SAMPLE_PERIOD - (read_end - read_start)
                    if time_to_sleep > 0:
                        time.sleep(time_to_sleep)
                bz.off()
            finally:
                bz.close() # RELEASE PIN 4 IMMEDIATELY for the web UI
            
            # --- PROCESSING ---
            rms = compute_rms(samples)
            db_spl = 20 * math.log10(rms / V_REF) if (rms > 0 and V_REF > 0) else -120.0

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(SOUND_DATA_FILE, "a") as f:
                f.write(f"{timestamp},{rms:.9f},{db_spl:.2f}\n")
                
            write_live_data({
                "timestamp": timestamp,
                "sound_rms": round(rms, 9),
                "sound_db": round(db_spl, 2)
            })
            write_heartbeat("sound_logger.json")

            next_cycle_start_time = cycle_start_time + CYCLE_INTERVAL_SEC
            if not FLIGHT_MODE:
                print(f"\rLogged {db_spl:.2f} dB SPL. Sleeping...", end="", flush=True)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nCRITICAL ERROR in main loop: {e}")
        raise # Allow the system to see the traceback

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SOUND_DATA_FILE):
        with open(SOUND_DATA_FILE, "w") as f:
            f.write("timestamp,rms_voltage(V),sound_level(dB SPL)\n") 
    
    # Startup Signal
    bz_start = get_buzzer_safe()
    bz_start.on(); time.sleep(0.2); bz_start.off(); bz_start.close()
    
    main_loop()

