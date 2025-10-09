# =========================================================================
# Kabot-1 Mission: Sound Logger (Flight-Ready with Heartbeat + ADS1115 + RMS + dB SPL)
# =========================================================================
# Logs RMS sound levels from a microphone connected to the Gravity 16-bit ADC.
# Outputs to CSV, updates central JSON, and emits a heartbeat file.
# =========================================================================

import time
from datetime import datetime
import os
import json
import math
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

# Reference voltage for dB SPL conversion (adjust after calibration)
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

# --- Main Functions ---

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

            # Compute RMS
            squares = [v**2 for v in samples]
            rms = math.sqrt(sum(squares) / len(squares))

            # Compute dB SPL (relative to V_REF)
            if rms > 0:
                db_spl = 20 * math.log10(rms / V_REF)
            else:
                db_spl = -math.inf  # silence

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

if __name__ == "__main__":
    main()
