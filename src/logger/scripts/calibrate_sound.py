# =========================================================================
# Kabot-1 Mission: Sound Logger Calibration Script
# =========================================================================
# Run this with a known SPL tone (e.g. 94 dB @ 1 kHz) to compute V_REF.
# =========================================================================

import time
import math
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Known calibration SPL (adjust if using a different calibrator)
SPL_REF = 94.0  # dB SPL

# Sampling parameters
SAMPLE_RATE = 100
WINDOW_SEC = 2
N = SAMPLE_RATE * WINDOW_SEC

# Initialize ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
chan = AnalogIn(ads, ADS.P0)

print("Collecting samples for calibration...")

samples = []
for _ in range(N):
    samples.append(chan.voltage)
    time.sleep(1.0 / SAMPLE_RATE)

# Compute RMS
squares = [v**2 for v in samples]
rms = math.sqrt(sum(squares) / len(squares))

# Compute calibrated V_REF
V_REF = rms / (10 ** (SPL_REF / 20))

print(f"Measured RMS Voltage: {rms:.6f} V")
print(f"Calibration SPL: {SPL_REF} dB")
print(f"Computed V_REF: {V_REF:.9f} V")

print("\nUpdate your sound_logger.py with this V_REF value for accurate dB SPL readings.")
