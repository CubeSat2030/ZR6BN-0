# connectivity_check.py
#
# Quick ping/SSH test to confirm AP is live.

#!/usr/bin/env python3
import subprocess

def check_ping():
    try:
        subprocess.run(["ping", "-c", "2", "192.168.4.1"], check=True)
        print("✅ Kabot-1 is reachable at 192.168.4.1")
    except subprocess.CalledProcessError:
        print("❌ Kabot-1 is not responding")

if __name__ == "__main__":
    check_ping()
