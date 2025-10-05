#!/usr/bin/env python3
"""
Entrypoint for Kabot-1 mission software.
Runs the MissionOrchestrator which handles sensors, detection, camera, email, webui, downlink.
"""
import logging
import signal
import sys
from src.mission.mission_orchestrator import MissionOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("main")

orc = None

def _signal(signum, frame):
    logger.info("Signal %s received — shutting down orchestrator", signum)
    if orc:
        orc.stop()
    sys.exit(0)

def main():
    global orc
    signal.signal(signal.SIGINT, _signal)
    signal.signal(signal.SIGTERM, _signal)
    orc = MissionOrchestrator()
    try:
        orc.run()
    except Exception:
        logger.exception("Fatal error in orchestrator")
    finally:
        orc.stop()

if __name__ == "__main__":
    main()
