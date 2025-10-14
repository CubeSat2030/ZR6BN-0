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
        # Use shell=False for security, pass command as a list
        result = subprocess.run(
            command,
            check=False, # We check manually
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
        
    # 2. Set the local device name (requires root for persistence/immediate change)
    if not run_command(["sudo", "bluetoothctl", "system-alias", DEVICE_NAME], f"Setting device name to {DEVICE_NAME}"):
        # Fallback to general alias setting if system-alias fails
        run_command(["sudo", "bluetoothctl", "alias", DEVICE_NAME], f"Setting temporary alias to {DEVICE_NAME}")

    # 3. Set discoverable and pairable (important for initial connection)
    run_command(["sudo", "bluetoothctl", "discoverable", "on"], "Enabling discoverable mode")
    run_command(["sudo", "bluetoothctl", "pairable", "on"], "Enabling pairable mode")
    
    # 4. Start the dedicated Bluetooth PAN service (Network Access Point)
    # This command relies on the 'bluetooth-network' service being available and configured 
    # to use 'panu' or 'nap' profiles correctly on the OS.
    # Note: 'bluetooth-network' is often required to be started via systemd/service manager.
    # If the system uses BlueZ 5+ and has 'bluetooth-network.service' enabled, this might be redundant, 
    # but we attempt to ensure the adapter's mode is correct for a host.
    if not run_command(["sudo", "hciconfig", BLUETOOTH_ADAPTER, "lm", "master", "iscan"], "Set Link Mode for host"):
         print("[WARNING] Could not set advanced link mode. Proceeding with default settings.")
         
    # Assuming 'pand' or a similar service is managed externally, 
    # we simply announce our readiness.
    print(f"[BEACON] Configuration complete. Advertising as '{DEVICE_NAME}'.")
    return True

def cleanup_beacon(signum, frame):
    """Gracefully resets Bluetooth state before exiting."""
    global ACTIVE
    ACTIVE = False
    print("\n[BEACON] Received termination signal. Starting cleanup...")
    
    # Resetting modes is crucial for future operations
    run_command(["sudo", "bluetoothctl", "discoverable", "off"], "Disabling discoverable mode")
    run_command(["sudo", "bluetoothctl", "pairable", "off"], "Disabling pairable mode")
    
    # Optionally reset name if necessary, but leaving the custom name is usually fine.
    # run_command(["sudo", "bluetoothctl", "system-alias", ""], "Resetting system alias")

    print("[BEACON] Cleanup complete. Exiting.")
    sys.exit(0)

def main():
    """Main execution loop for the beacon script."""
    global ACTIVE
    
    # Setup signal handlers for graceful termination from app_server.py
    signal.signal(signal.SIGINT, cleanup_beacon)
    signal.signal(signal.SIGTERM, cleanup_beacon)

    if not setup_beacon():
        print("[BEACON] Initial setup failed. Exiting script.")
        return

    print("[BEACON] Hotspot is active. Running until stopped via dashboard...")
    
    # Main loop runs while waiting for client connection or dashboard stop command
    while ACTIVE:
        # Simple loop to keep the script alive and the hotspot active.
        # This prevents the parent process (app_server.py) from thinking it crashed.
        try:
            time.sleep(1) 
        except Exception:
            # Handle possible interruption during sleep (e.g., SIGINT/SIGTERM)
            break

    # Final explicit cleanup if loop breaks for unexpected reason
    if ACTIVE:
        cleanup_beacon(None, None) 

if __name__ == "__main__":
    main()

