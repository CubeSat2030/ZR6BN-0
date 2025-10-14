# -*- coding: utf-8 -*-
"""
Kabot-1 Bluetooth PAN Hotspot Beacon Script (src/beacon.py)
Refactored with RF-kill detection and clearer diagnostics.
"""

import subprocess
import time
import sys
import signal

# --- Configuration ---
DEVICE_NAME = "Kabot-1"
BLUETOOTH_ADAPTER = "hci0"
PAN_SERVICE_NAME = "KabotSat"

# --- Global State ---
ACTIVE = True

def run_command(command, description="Command", fatal=False):
    """Executes a shell command with logging and error handling."""
    print(f"[BEACON] Executing: {description} -> {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
        else:
            print(f"[ERROR] {description} failed (Code {result.returncode})")
            if result.stdout.strip():
                print(f"  STDOUT: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"  STDERR: {result.stderr.strip()}")
            if fatal:
                sys.exit(1)
            return False
    except Exception as e:
        print(f"[ERROR] {description} exception: {e}")
        if fatal:
            sys.exit(1)
        return False

def check_and_unblock_rfkill():
    """Detects and unblocks RF-kill if Bluetooth is blocked."""
    print("[BEACON] Checking RF-kill status...")
    result = subprocess.run(["rfkill", "list"], capture_output=True, text=True)
    if "bluetooth" not in result.stdout.lower():
        print("[WARNING] No Bluetooth device found in rfkill list.")
        return True  # Not fatal, may still work

    if "Soft blocked: yes" in result.stdout or "Hard blocked: yes" in result.stdout:
        print("[WARNING] Bluetooth is blocked. Attempting to unblock...")
        if run_command(["sudo", "rfkill", "unblock", "bluetooth"], "Unblocking Bluetooth"):
            print("[BEACON] RF-kill unblock attempted. Re-check with 'rfkill list'.")
            return True
        else:
            print("[FATAL] Unable to unblock Bluetooth. Manual intervention required.")
            return False
    print("[BEACON] RF-kill check passed. Bluetooth not blocked.")
    return True

def setup_beacon():
    """Configures the Bluetooth adapter and starts the network service."""
    print(f"[BEACON] Starting setup for {DEVICE_NAME}...")

    if not check_and_unblock_rfkill():
        return False

    if not run_command(["sudo", "hciconfig", BLUETOOTH_ADAPTER, "up"], "Powering up adapter"):
        return False

    run_command(["sudo", "bluetoothctl", "system-alias", DEVICE_NAME], f"Setting device name to {DEVICE_NAME}")
    run_command(["sudo", "bluetoothctl", "discoverable", "on"], "Enabling discoverable mode")
    run_command(["sudo", "bluetoothctl", "pairable", "on"], "Enabling pairable mode")

    if not run_command(["sudo", "hciconfig", BLUETOOTH_ADAPTER, "lm", "master", "iscan"], "Set Link Mode for host"):
        print("[WARNING] Could not set advanced link mode. Proceeding with defaults.")

    print(f"[BEACON] Configuration complete. Advertising as '{DEVICE_NAME}'.")
    return True

def cleanup_beacon(signum, frame):
    """Gracefully resets Bluetooth state before exiting."""
    global ACTIVE
    ACTIVE = False
    print("\n[BEACON] Received termination signal. Starting cleanup...")
    run_command(["sudo", "bluetoothctl", "discoverable", "off"], "Disabling discoverable mode")
    run_command(["sudo", "bluetoothctl", "pairable", "off"], "Disabling pairable mode")
    run_command(["sudo", "hciconfig", BLUETOOTH_ADAPTER, "down"], "Powering down adapter")
    print("[BEACON] Cleanup complete. Exiting.")
    sys.exit(0)

def main():
    global ACTIVE
    signal.signal(signal.SIGINT, cleanup_beacon)
    signal.signal(signal.SIGTERM, cleanup_beacon)

    if not setup_beacon():
        print("[BEACON] Initial setup failed. Exiting script.")
        return

    print("[BEACON] Hotspot is active. Running until stopped via dashboard...")
    heartbeat = 0
    while ACTIVE:
        try:
            time.sleep(5)
            heartbeat += 1
            if heartbeat % 12 == 0:  # Every minute
                print("[BEACON] Heartbeat: beacon still active.")
        except Exception:
            break

    if ACTIVE:
        cleanup_beacon(None, None)

if __name__ == "__main__":
    main()
