"""
Touchdown detector — conservative logic to avoid false positives.

Criteria:
- If impact magnitude >= impact_threshold_g OR
- Sustained low altitude (<= alt_threshold) AND low motion for debounce seconds
"""
import time
import logging
from threading import Event, Thread
from typing import Callable

logger = logging.getLogger("touchdown_detector")

class TouchdownDetector(Thread):
    def __init__(self, datastore, on_touchdown: Callable[[dict], None],
                 impact_threshold_g=3.0, alt_threshold_m=5.0, motion_threshold_g=0.6,
                 debounce_s=8.0, poll_interval=0.5):
        super().__init__(daemon=True)
        self.ds = datastore
        self.on_touchdown = on_touchdown
        self.impact_threshold = impact_threshold_g
        self.alt_threshold = alt_threshold_m
        self.motion_threshold = motion_threshold_g
        self.debounce = debounce_s
        self.poll = poll_interval
        self._stop = Event()
        self._candidate_start = None
        self._confirmed = False

    def stop(self):
        self._stop.set()

    def _mag(self, accel):
        try:
            x = float(accel.get("x",0)); y=float(accel.get("y",0)); z=float(accel.get("z",0))
            mag = (x*x + y*y + z*z)**0.5
            if mag > 20:
                mag = mag / 9.80665
            return mag
        except Exception:
            return 0.0

    def run(self):
        logger.info("TouchdownDetector started")
        while not self._stop.is_set():
            latest = self.ds.read_all()
            candidate = False
            reason = None
            # impact check
            mpu = latest.get("mpu6050")
            if mpu and "accel" in mpu:
                mag = self._mag(mpu["accel"])
                if mag >= self.impact_threshold:
                    candidate = True
                    reason = f"impact_{mag:.2f}g"

            # low altitude check
            gps = latest.get("gps")
            if gps and ('alt' in gps or 'altitude' in gps):
                alt = gps.get("alt") or gps.get("altitude")
                try:
                    if float(alt) <= self.alt_threshold:
                        candidate = True
                        reason = "gps_low_alt"
                except Exception:
                    pass
            else:
                bmp = latest.get("bmp280")
                if bmp and "pressure" in bmp:
                    # If user provided pressure threshold in config, can be used. Omitted here.
                    pass

            # debounce + motion check
            if candidate:
                if self._candidate_start is None:
                    self._candidate_start = time.time()
                else:
                    elapsed = time.time() - self._candidate_start
                    # check motion stable
                    motion_ok = True
                    if mpu and "accel" in mpu:
                        mag_now = self._mag(mpu["accel"])
                        if mag_now > self.motion_threshold:
                            motion_ok = False
                    if elapsed >= self.debounce and motion_ok and not self._confirmed:
                        self._confirmed = True
                        event = {"timestamp": time.time(), "reason": reason, "elapsed": elapsed}
                        logger.info("Touchdown confirmed: %s", event)
                        try:
                            self.on_touchdown(event)
                        except Exception:
                            logger.exception("on_touchdown handler failed")
            else:
                self._candidate_start = None
            time.sleep(self.poll)
        logger.info("TouchdownDetector stopped")
