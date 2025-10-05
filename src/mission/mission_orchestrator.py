"""
High-level orchestrator coordinating detectors, camera, email, webui, and downlink.

Sequence:
- Start sensor listeners and detectors
- On launch: capture image, email it, stop webui/downlink (if running)
- On touchdown: capture image, email it (include GPS coords), start webui/downlink and queue uploads

Configuration via environment variables (see email_notifier docs).
"""
import os
import logging
import threading
import time
from pathlib import Path

from src.logger.utils import LatestDataStore
from src.photography.image_capture import capture_image
from src.network.email_notifier import send_email
from src.network.net_utils import get_best_bind_ip
from src.network.downlink import DownlinkManager  # will create below
from src.mission.launch_detector import LaunchDetector
from src.mission.touchdown_detector import TouchdownDetector
from src.web_ui.app_server import WebUI

logger = logging.getLogger("mission_orchestrator")

class MissionOrchestrator:
    def __init__(self):
        self.ds = LatestDataStore()
        self.webui = WebUI(host=get_best_bind_ip(), port=int(os.environ.get("KABOT_WEB_PORT", 5000)),
                           data_file=self.ds.latest_file_path,
                           template_folder=Path(__file__).resolve().parent.parent.joinpath("web_ui","templates"))
        self.downlink = DownlinkManager(endpoint_url=os.environ.get("KABOT_ENDPOINT"))
        # sensor listeners expected to be present in src/sensors or src/downlink/event_listeners
        from src.downlink.event_listeners.mpu6050_event_listener import MPU6050EventListener
        from src.downlink.event_listeners.bmp280_event_listener import BMP280EventListener
        self.mpu = MPU6050EventListener(callback=lambda d: self.ds.update("mpu6050", d))
        self.bmp = BMP280EventListener(callback=lambda d: self.ds.update("bmp280", d))
        # optional gps listener, if present in your repo it should update 'gps' key
        try:
            from src.tracking.gps import GPSReader
            self.gps_reader = GPSReader()
            # spawn simple GPS poller thread
        except Exception:
            self.gps_reader = None
        self.launch_detector = LaunchDetector(self.ds, on_launch=self._on_launch)
        self.touch_detector = TouchdownDetector(self.ds, on_touchdown=self._on_touchdown)
        self._threads = []
        self._running = False
        self._launched = False
        self._touched = False

    # ---------- lifecycle ----------
    def run(self):
        logger.info("Mission orchestrator starting")
        self._running = True
        # start sensor listeners
        t_mpu = threading.Thread(target=self.mpu.start, kwargs={"interval": 0.5}, daemon=True)
        t_bmp = threading.Thread(target=self.bmp.start, kwargs={"interval": 1.0}, daemon=True)
        t_mpu.start(); t_bmp.start()
        self._threads += [t_mpu, t_bmp]
        # start detectors
        self.launch_detector.start()
        self.touch_detector.start()
        # optional GPS poller
        if self.gps_reader:
            t_gps = threading.Thread(target=self._gps_loop, daemon=True)
            t_gps.start()
            self._threads.append(t_gps)
        # start web UI initially bound to BT PAN but keep it running until launch detection says stop? 
        # per your request: Web UI should be inactive during flight. Start it now but will shut at launch.
        try:
            # We'll start it so you can configure prior to flight; comment out if you don't want it running preflight.
            self.webui.start()
        except Exception:
            logger.exception("Web UI start failed")
        # main keepalive
        while self._running:
            try:
                # persist lightweight telemetry each 10s
                payload = {"timestamp": time.time(), "latest": self.ds.read_all(), "launched": self._launched, "touched": self._touched}
                self.ds.persist_payload(payload)
                time.sleep(10)
            except Exception:
                logger.exception("Orchestrator loop error")
                time.sleep(5)

    def stop(self):
        logger.info("Mission orchestrator stopping")
        self._running = False
        try:
            self.launch_detector.stop()
        except:
            pass
        try:
            self.touch_detector.stop()
        except:
            pass
        try:
            self.mpu.stop()
        except:
            pass
        try:
            self.bmp.stop()
        except:
            pass
        try:
            if self.gps_reader:
                self.gps_reader.ser and self.gps_reader.ser.close()
        except:
            pass
        # do not forcibly stop webui/downlink here; they can be stopped
        try:
            self.webui.stop()
        except:
            pass
        try:
            self.downlink.stop()
        except:
            pass
        logger.info("Mission orchestrator stopped")

    # ---------- gps poller ----------
    def _gps_loop(self):
        logger.info("GPS poller started")
        while self._running:
            try:
                fix = self.gps_reader.get_fix()
                if fix:
                    self.ds.update("gps", fix)
                time.sleep(2)
            except Exception:
                logger.exception("GPS poller error")
                time.sleep(2)

    # ---------- event handlers ----------
    def _on_launch(self, event):
        """
        Called once on confirmed launch. Actions:
         - capture image
         - send email (launch image)
         - stop webui and downlink to save power (per request)
        """
        if self._launched:
            return
        self._launched = True
        logger.info("Handling launch event: %s", event)
        try:
            img = capture_image(filename=f"launch_{int(time.time())}.jpg")
            subject = "Kabot-1 Launch Detected"
            latlon = self.ds.read_all().get("gps")
            body = f"Launch detected at {time.ctime(event['timestamp'])}.\nReason: {event.get('reason')}\nGPS: {latlon}\n"
            # send email (smtp preferred, sim fallback used inside send_email)
            if send_email(subject, body, attachments=[img]):
                logger.info("Launch email sent")
            else:
                logger.warning("Launch email failed to send")
        except Exception:
            logger.exception("Launch email or capture failed")

        # stop web UI & downlink to preserve power while climbing
        try:
            logger.info("Stopping Web UI and Downlink for flight mode")
            self.webui.stop()
        except Exception:
            logger.exception("Failed to stop webui")
        try:
            self.downlink.stop()
        except Exception:
            logger.exception("Failed to stop downlink")

    def _on_touchdown(self, event):
        """
        Called once on confirmed touchdown. Actions:
         - capture image
         - send email with image and GPS coordinates
         - start web ui and downlink and queue upload of logs+media
        """
        if self._touched:
            return
        self._touched = True
        logger.info("Handling touchdown: %s", event)
        try:
            img = capture_image(filename=f"touchdown_{int(time.time())}.jpg")
            latest = self.ds.read_all()
            gps = latest.get("gps", {})
            coords = f"{gps.get('lat')},{gps.get('lon')}" if gps else "unknown"
            subject = "Kabot-1 Touchdown Confirmed"
            body = f"Touchdown at {time.ctime(event['timestamp'])}\nReason: {event.get('reason')}\nGPS: {coords}\nFull latest: {latest}\n"
            if send_email(subject, body, attachments=[img]):
                logger.info("Touchdown email sent")
            else:
                logger.warning("Touchdown email failed")
        except Exception:
            logger.exception("Touchdown email/capture failed")

        # start webui & downlink
        try:
            logger.info("Starting Web UI and Downlink to allow retrieval")
            self.webui.start()
        except Exception:
            logger.exception("Failed to start webui")
        try:
            self.downlink.start()
        except Exception:
            logger.exception("Failed to start downlink")
        # queue all files for upload
        try:
            from src.network.upload_utils import queue_all_files_for_upload
            queue_all_files_for_upload(self.downlink)
        except Exception:
            # fallback: simple queue mechanism if upload_utils missing: queue latest file indicators
            logger.exception("Failed to queue files via upload_utils; consider adding that module")
