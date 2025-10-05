"""
Shared data store and logging utilities.
Keeps LATEST_SENSOR_DATA.json and archives payload files.
"""
import json
import logging
import time
from pathlib import Path
from threading import Lock

logger = logging.getLogger("logger.utils")

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE.joinpath("data")
ARCHIVE_DIR = DATA_DIR.joinpath("archives")
DATA_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
LATEST_FILE = DATA_DIR.joinpath("LATEST_SENSOR_DATA.json")

class LatestDataStore:
    def __init__(self):
        self._lock = Lock()
        self._data = {}
        self.latest_file_path = LATEST_FILE

    def update(self, key: str, value: dict):
        with self._lock:
            self._data[key] = value
            # write incremental update (keep operations small)
            try:
                existing = {}
                if self.latest_file_path.exists():
                    existing = json.loads(self.latest_file_path.read_text())
                existing[key] = value
                self.latest_file_path.write_text(json.dumps(existing))
            except Exception:
                logger.exception("Failed to update latest JSON")

    def read_all(self) -> dict:
        with self._lock:
            return dict(self._data)

    def persist_payload(self, payload: dict):
        ts = int(time.time())
        out = ARCHIVE_DIR.joinpath(f"{ts}.json")
        try:
            out.write_text(json.dumps(payload))
            # also update last_payload key
            cur = {}
            if self.latest_file_path.exists():
                try:
                    cur = json.loads(self.latest_file_path.read_text())
                except:
                    cur = {}
            cur["last_payload"] = payload
            self.latest_file_path.write_text(json.dumps(cur))
        except Exception:
            logger.exception("Failed to persist payload")
