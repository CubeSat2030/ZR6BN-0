# =========================================================================
# Kabot I Flight Controller (main.py) - Actual Flight Code Placeholder
# =========================================================================
# This script is launched by the Web Server's auto-start mechanism 
# or manual trigger. It represents the core flight control loop.
# =========================================================================

import time
import signal
import sys
import threading

# --- Placeholder Flight Loop ---
def flight_loop():
    print("[FLIGHT CONTROLLER] Flight control loop started. Running until terminated...")
    try:
        while True:
            # In a real system, this would be the main control logic
            # For now, it just prints a heartbeat.
            # print(f"[FLIGHT HEARTBEAT] Time: {time.time()}")
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\n[FLIGHT CONTROLLER] Received SIGINT. Shutting down gracefully.")
    except Exception as e:
        print(f"\n[FLIGHT CONTROLLER ERROR] Unhandled exception: {e}")
    finally:
        print("[FLIGHT CONTROLLER] Loop finished.")

def main():
    # Set a custom signal handler for SIGTERM (used by the server to stop)
    def terminate_handler(signum, frame):
        print("\n[FLIGHT CONTROLLER] Received SIGTERM/SIGINT. Exiting.")
        sys.exit(0)

    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)

    flight_loop()

if __name__ == "__main__":
    main()
