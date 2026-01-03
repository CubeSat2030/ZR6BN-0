# =========================================================================
# Kabot-1 Mission: Heartbeat Utility
# =========================================================================
# Provides a simple function to write heartbeat JSON files for monitored
# loggers. Each logger should call write_heartbeat("<name>.json") once per
# cycle to signal liveness to the master launcher.
# =========================================================================

import os
import json
from datetime import datetime

HEARTBEAT_DIR = os.path.join("src", "logger", "heartbeats")
os.makedirs(HEARTBEAT_DIR, exist_ok=True)

def write_heartbeat(filename: str):
    """
    Write a heartbeat JSON file with the current timestamp.
    
    Args:
        filename (str): The name of the heartbeat file, e.g. "cpu_logger.json"
    """
    hb_path = os.path.join(HEARTBEAT_DIR, filename)
    try:
        with open(hb_path, "w") as f:
            json.dump({"last_heartbeat": datetime.now().isoformat()}, f)
    except Exception:
        # Fail silently in flight mode
        pass
