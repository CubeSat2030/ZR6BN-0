# kabot1_hotspot.py
#
# ython script that configures and launches the AP (SSID: Kabot‑1

#!/usr/bin/env python3
import subprocess
import sys
import logging
from pathlib import Path

# Setup logging
log_file = Path(__file__).resolve().parents[1] / "logs" / "ap_startup.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

def run(cmd):
    logging.info(f"Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {cmd}\n{e}")
        sys.exit(1)

def setup_ap():
    # Assign static IP
    run("ip addr add 192.168.4.1/24 dev wlan0 || true")
    run("ip link set wlan0 up")

    # Start hostapd and dnsmasq using configs in kabot_launchpad/configs
    configs_dir = Path(__file__).resolve().parents[1] / "configs"
    hostapd_conf = configs_dir / "hostapd.conf"
    dnsmasq_conf = configs_dir / "dnsmasq.conf"

    run(f"hostapd {hostapd_conf} -B")
    run(f"dnsmasq --conf-file={dnsmasq_conf}")

    logging.info("Access Point Kabot-1 started successfully.")
    print("✅ Kabot-1 hotspot is live at 192.168.4.1")

if __name__ == "__main__":
    setup_ap()

