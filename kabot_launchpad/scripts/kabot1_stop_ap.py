# kabot1_stop_ap.py
#
# This script is used to gracefully shut down hostapd/dnsmasq.

#!/usr/bin/env python3
import subprocess
import logging
from pathlib import Path

log_file = Path(__file__).resolve().parents[1] / "logs" / "ap_startup.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

def run(cmd):
    logging.info(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)

def stop_ap():
    run("pkill hostapd")
    run("pkill dnsmasq")
    logging.info("Access Point Kabot-1 stopped.")
    print("🛑 Kabot-1 hotspot has been stopped.")

if __name__ == "__main__":
    stop_ap()
