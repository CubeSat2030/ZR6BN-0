"""
Downlink manager: queue-based uploader. Supports:
- HTTP POST to endpoint (requests)
- You can extend to use SIM7600 AT HTTP sequences for cellular upload.

DownlinkManager is purposely simple: it starts only when orchestrator calls `start`.
"""
import json
import logging
import threading
import time
from queue import Queue, Empty

logger = logging.getLogger("network.downlink")

try:
    import requests
except Exception:
    requests = None

class DownlinkManager:
    def __init__(self, endpoint_url: str = None):
        self.endpoint = endpoint_url
        self._q = Queue()
        self._thread = None
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("DownlinkManager started")

    def stop(self):
        self._running = False
        logger.info("DownlinkManager stopping")

    def is_running(self):
        return self._running

    def queue_payload(self, payload: dict):
        try:
            self._q.put_nowait(payload)
        except Exception:
            logger.exception("Failed to queue payload")

    def _send_http(self, payload: dict) -> bool:
        if not self.endpoint:
            logger.warning("No endpoint configured for downlink")
            return False
        if not requests:
            logger.warning("requests not installed; cannot send HTTP payloads")
            return False
        try:
            r = requests.post(self.endpoint, json=payload, timeout=20)
            logger.info("Downlink HTTP status %s for payload", r.status_code)
            return r.status_code in (200,201,202)
        except Exception:
            logger.exception("HTTP send failed")
            return False

    def _loop(self):
        while self._running:
            try:
                payload = self._q.get(timeout=1)
            except Empty:
                time.sleep(0.1)
                continue
            sent = False
            for attempt in range(3):
                sent = self._send_http(payload)
                if sent:
                    break
                time.sleep(5)
            if not sent:
                logger.warning("Failed to send payload after retries, requeueing")
                try:
                    self._q.put_nowait(payload)
                except Exception:
                    logger.exception("Requeue failed")
            self._q.task_done()
            time.sleep(0.2)
