# =========================================================================
# Kabot-1 Mission: Sound Logger
# =========================================================================
# Modes:
#   --calibrate : Run calibration with known SPL tone (e.g. 94 dB @ 1 kHz).
#   default     : Log RMS sound levels (volts + dB SPL) with heartbeat.
# =========================================================================

import time
from datetime import datetime
import os
import json
import math
import sys
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from heartbeat import write_heartbeat

# --- Configuration ---
FLIGHT_MODE = True  # Silence console output during flight

DATA_DIR = os.path.join("src", "logger", "data")
DATA_FILE = os.path.join(DATA_DIR, "SOUND.txt")
LIVE_DATA_FILE = os.path.join(DATA_DIR, "LATEST_SENSOR_DATA.json")

SCRIPT_START_TIME = datetime.now()

# Default reference voltage (will be updated after calibration)
V_REF = 1.0  # volts RMS

# --- Initialize I2C and ADC ---
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1  # ±4.096V range
chan = AnalogIn(ads, ADS.P0)  # Microphone connected to channel A0

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

def compute_rms(samples):
    """Compute RMS from a list of voltage samples."""
    if not samples:
        return 0.0
    squares = [v**2 for v in samples]
    return math.sqrt(sum(squares) / len(squares))

# --- Calibration Mode ---

def calibrate(spl_ref=94.0, sample_rate=100, window_sec=2):
    """Calibrate V_REF using a known SPL tone."""
    N = sample_rate * window_sec
    print(f"Collecting {N} samples for calibration...")

    samples = []
    for _ in range(N):
        samples.append(chan.voltage)
        time.sleep(1.0 / sample_rate)

    rms = compute_rms(samples)
    v_ref = rms / (10 ** (spl_ref / 20))

    print(f"\nCalibration Results:")
    print(f"  Measured RMS Voltage: {rms:.6f} V")
    print(f"  Calibration SPL: {spl_ref} dB")
    print(f"  Computed V_REF: {v_ref:.9f} V")
    print("\nUpdate V_REF in this script with the computed value for accurate dB SPL logging.")

# --- Logging Mode ---

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("timestamp,sound_rms(volts),sound_db(dB SPL)\n")

    if not FLIGHT_MODE:
        print(f"Sound Logger active. Logging RMS + dB SPL to {DATA_FILE}.")
    main_loop()

def main_loop():
    try:
        SAMPLE_RATE = 100   # samples per second
        WINDOW_SEC = 1      # RMS window length
        N = SAMPLE_RATE * WINDOW_SEC

        while True:
            samples = []
            for _ in range(N):
                samples.append(chan.voltage)
                time.sleep(1.0 / SAMPLE_RATE)

            rms = compute_rms(samples)

            # Compute dB SPL (relative to calibrated V_REF)
            if rms > 0 and V_REF > 0:
                db_spl = 20 * math.log10(rms / V_REF)
            else:
                db_spl = -math.inf

            timestamp = datetime.now().strftime("%H:%M:%S")
            with open(DATA_FILE, "a") as f:
                f.write(f"{timestamp},{rms:.6f},{db_spl:.2f}\n")

            data_point = {
                "timestamp": timestamp,
                "sound_rms": round(rms, 6),
                "sound_db": None if db_spl == -math.inf else round(db_spl, 2)
            }
            write_live_data(data_point)
            write_heartbeat("sound_logger.json")

            if not FLIGHT_MODE:
                print(f"\rLogged RMS: {rms:.6f} V | {db_spl:.2f} dB at {timestamp}", end="", flush=True)

    except KeyboardInterrupt:
        if not FLIGHT_MODE:
            print("\nSound logging terminated.")

# --- Entry Point ---

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--calibrate":
        calibrate()
    else:
        main()
