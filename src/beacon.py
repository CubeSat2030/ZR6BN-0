# -*- coding: utf-8 -*-
"""
Kabot-1 Bluetooth PAN Hotspot Beacon Script (src/beacon.py)

This script is launched by the Mission Control Dashboard to activate the 
Bluetooth Personal Area Network (PAN) Hotspot, allowing the KabotSat 
client application to connect and establish a dedicated link with the 
Kabot-1 payload.

It requires 'sudo' privileges for system-level Bluetooth and networking commands.
"""

import subprocess
import time
import sys
import signal

# --- Configuration ---
DEVICE_NAME = "Kabot-1"
BLUETOOTH_ADAPTER = "hci0" # Default adapter name
PAN_SERVICE_NAME = "KabotSat" # Placeholder for a dedicated service identifier

# --- Global State ---
ACTIVE = True

def run_command(command, description="Command"):
    """
    Executes a shell command using subprocess and checks for errors.
    Returns True on success, False otherwise.
    """
    print(f"[BEACON] Executing: {description} ('{' '.join(command)}')")
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
            print(f"[ERROR] {description} failed (Code {result.returncode}):")
            print(f"  STDOUT: {result.stdout.strip()}")
            print(f"  STDERR: {result.stderr.strip()}")
            return False
            
    except FileNotFoundError:
        print(f"[ERROR] Required command not found: {command[0]}")
        return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {description} timed out.")
        return False
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during {description}: {e}")
        return False

def setup_beacon():
    """Configures the Bluetooth adapter and starts the network service."""
    print(f"[BEACON] Starting setup for {DEVICE_NAME}...")

    # 1. Ensure Bluetooth Adapter is powered on
    if not run_command(["sudo", "hciconfig", BLUETOOTH_ADAPTER, "up"], "Powering up adapter"):
        return False
        
    # 2. Set the local device name
    if not run_command(["sudo", "bluetoothctl", "system-alias", DEVICE_NAME], f"Setting device name to {DEVICE_NAME}"):
        run_command(["sudo", "bluetoothctl", "alias", DEVICE_NAME], f"Setting temporary alias to {DEVICE_NAME}")

    # 3. Set discoverable and pairable
    run_command(["sudo", "bluetoothctl", "discoverable", "on"], "Enabling discoverable mode")
    run_command(["sudo", "bluetoothctl", "pairable", "on"], "Enabling pairable mode")
    
    # 4. Set link mode (optional)
    if not run_command(["sudo", "hciconfig", BLUETOOTH_ADAPTER, "lm", "master", "iscan"], "Set Link Mode for host"):
         print("[WARNING] Could not set advanced link mode. Proceeding with default settings.")
         
    print(f"[BEACON] Configuration complete. Advertising as '{DEVICE_NAME}'.")
    return True

def cleanup_beacon(signum, frame):
    """Gracefully resets Bluetooth state before exiting."""
    global ACTIVE
    ACTIVE = False
    print("\n[BEACON] Received termination signal. Starting cleanup...")
    run_command(["sudo", "bluetoothctl", "discoverable", "off"], "Disabling discoverable mode")
    run_command(["sudo", "bluetoothctl", "pairable", "off"], "Disabling pairable mode")
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
    while ACTIVE:
        try:
            time.sleep(1) 
        except Exception:
            break

    if ACTIVE:
        cleanup_beacon(None, None) 

if __name__ == "__main__":
    main()
