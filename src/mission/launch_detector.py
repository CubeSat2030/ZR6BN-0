"""
Detects launch (takeoff) and triggers a callback.

Strategy:
- Consider launch when:
  - sustained upward trend in barometric pressure -> decrease in pressure (altitude rising)
  OR
  - sustained acceleration magnitude above a threshold
- Debounce: condition must hold for `debounce_s` continuous seconds.
"""
import time
import logging
from threading import Event, Thread
from typing import Callable

logger = logging.getLogger("launch_detector")

class LaunchDetector(Thread):
    def __init__(self, datastore, on_launch: Callable[[dict], None],
                 accel_threshold_g=2.0, baro_drop_hpa=1.5, debounce_s=6.0, poll_interval=0.5):
        super().__init__(daemon=True)
        self.ds = datastore
        self.on_launch = on_launch
        self.accel_threshold = accel_threshold_g
        self.baro_drop = baro_drop_hpa
        self.debounce = debounce_s
        self.poll = poll_interval
        self._stop = Event()
        self._candidate_start = None
        self._baseline_pressure = None
        self._launched = False

    def stop(self):
        self._stop.set()

    def run(self):
        logger.info("LaunchDetector started")
        # establish baseline pressure from first few readings
        baseline_samples = []
        start_time = time.time()
        while not self._stop.is_set() and time.time()-start_time < 5:
            latest = self.ds.read_all()
            bmp = latest.get("bmp280")
            if bmp and "pressure" in bmp:
                baseline_samples.append(float(bmp["pressure"]))
            time.sleep(0.5)
        if baseline_samples:
            self._baseline_pressure = sum(baseline_samples)/len(baseline_samples)
            logger.info("LaunchDetector baseline pressure %.2f hPa", self._baseline_pressure)
        else:
            logger.info("LaunchDetector no baseline pressure available")

        while not self._stop.is_set():
            latest = self.ds.read_all()
            candidate = False
            reason = None
            # acceleration check
            mpu = latest.get("mpu6050")
            if mpu and "accel" in mpu:
                a = mpu["accel"]
                mag = (a.get("x",0)**2 + a.get("y",0)**2 + a.get("z",0)**2)**0.5
                # if units are m/s^2 convert to g
                if mag > 20:
                    mag = mag / 9.80665
                if mag >= self.accel_threshold:
                    candidate = True
                    reason = f"accel_mag={mag:.2f}g"

            # barometric ascent detection: pressure drop by threshold
            bmp = latest.get("bmp280")
            if bmp and "pressure" in bmp and self._baseline_pressure:
                pressure = float(bmp["pressure"])
                if self._baseline_pressure - pressure >= self.baro_drop:
                    candidate = True
                    reason = f"baro_drop={self._baseline_pressure - pressure:.2f}"

            if candidate:
                if self._candidate_start is None:
                    self._candidate_start = time.time()
                    logger.debug("Launch candidate started: %s", reason)
                else:
                    if time.time() - self._candidate_start >= self.debounce and (not self._launched):
                        self._launched = True
                        event = {"timestamp": time.time(), "reason": reason}
                        logger.info("Launch confirmed: %s", event)
                        try:
                            self.on_launch(event)
                        except Exception:
                            logger.exception("on_launch handler failed")
            else:
                self._candidate_start = None
            time.sleep(self.poll)
        logger.info("LaunchDetector stopped")
