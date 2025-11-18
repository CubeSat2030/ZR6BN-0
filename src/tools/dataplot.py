import tkinter as tk
from tkinter import ttk
import math, time, random, threading
from datetime import datetime

# --- Mission parameters (metadata displayed, not embedded in data rows) ---
MISSION_DATE = datetime.now().strftime("%Y-%m-%d")
MISSION_START = datetime.now().strftime("%H:%M:%S")
MISSION_LAND = "12:45:00"  # set as needed
PAYLOAD_DIMENSIONS = (0.30, 0.20, 0.15)  # meters (x, y, z)
BALLOON_BURST_ALTITUDE = 32000  # meters
CHUTE_DEPLOYMENT = False

# --- Simulation parameters ---
SAMPLE_RATE_HZ = 10          # samples per second
SIM_DURATION_S = 120         # total duration (seconds)
mass = 2.0                   # kg payload
# Moments of inertia for a rectangular box about principal axes
Ix = (1/12)*mass*(PAYLOAD_DIMENSIONS[1]**2 + PAYLOAD_DIMENSIONS[2]**2)
Iy = (1/12)*mass*(PAYLOAD_DIMENSIONS[0]**2 + PAYLOAD_DIMENSIONS[2]**2)
Iz = (1/12)*mass*(PAYLOAD_DIMENSIONS[0]**2 + PAYLOAD_DIMENSIONS[1]**2)

# --- Weather parameters (affect physics) ---
weather = {
    "wind_speed": 15.0,        # m/s baseline wind influence
    "turbulence": 0.2,         # 0–1 stochastic perturbation magnitude
    "temperature_bias": 0.001  # gyro drift per °C (bias term)
}

running = False

# --- International Standard Atmosphere (ISA) approximation ---
def atmosphere(alt_m):
    """
    Returns (T °C, P Pa, rho kg/m^3) for altitude alt_m.
    Piecewise ISA approximation (troposphere, lower/upper stratosphere).
    """
    if alt_m < 11000.0:  # Troposphere
        T = 15.04 - 0.00649 * alt_m
        P = 101290.0 * ((T + 273.1) / 288.08) ** 5.256
    elif alt_m < 25000.0:  # Lower stratosphere (isothermal)
        T = -56.46
        P = 22650.0 * math.exp(1.73 - 0.000157 * alt_m)
    else:  # Upper stratosphere
        T = -131.21 + 0.00299 * alt_m
        P = 2488.0 * ((T + 273.1) / 216.6) ** -11.388
    rho = P / (287.05 * (T + 273.15))  # ideal gas law with R = 287.05 J/(kg·K)
    return T, P, rho

def altitude_profile(t_s):
    """
    Ascent at ~5 m/s until burst, then descent without chute at ~50 m/s.
    t_s is simulation time in seconds.
    """
    ascent_rate = 5.0     # m/s (typical)
    descent_rate = 50.0   # m/s (no chute, tumbling)
    t_burst = BALLOON_BURST_ALTITUDE / ascent_rate
    if t_s <= t_burst:
        return ascent_rate * t_s
    else:
        return max(0.0, BALLOON_BURST_ALTITUDE - descent_rate * (t_s - t_burst))

def angular_velocity(t_s, alt_m):
    """
    Physics-based angular velocity ω = (wx, wy, wz) in rad/s:
    - Pre-burst: damped oscillations + wind-induced rotation
    - Post-burst: chaotic tumbling with higher frequencies
    - Weather: wind adds torque; turbulence adds small random perturbations
    - Atmosphere: air density provides damping; temperature induces bias drift
    """
    T, P, rho = atmosphere(alt_m)

    # Base motion: pre-burst oscillation, post-burst tumble
    if alt_m < BALLOON_BURST_ALTITUDE:
        wx = (20.0 * math.sin(0.5 * t_s) + weather["wind_speed"] * 0.5) / Ix
        wy = (15.0 * math.cos(0.3 * t_s) + weather["wind_speed"] * 0.3) / Iy
        wz = (10.0 * math.sin(0.2 * t_s)) / Iz
    else:
        wx = (100.0 * math.sin(2.0 * t_s) + weather["wind_speed"]) / Ix
        wy = (120.0 * math.cos(1.5 * t_s) + weather["wind_speed"] * 0.8) / Iy
        wz = (90.0 * math.sin(1.2 * t_s)) / Iz

    # Turbulence (stochastic perturbation)
    turb = weather["turbulence"]
    wx += random.uniform(-turb, turb)
    wy += random.uniform(-turb, turb)
    wz += random.uniform(-turb, turb)

    # Temperature-dependent bias drift
    drift = T * weather["temperature_bias"]
    wx += drift; wy += drift; wz += drift

    # Air density damping (less dense → less damping). Normalize to sea level ~1.225 kg/m^3.
    damping = max(0.05, min(1.0, rho / 1.225))
    wx *= damping; wy *= damping; wz *= damping

    return wx, wy, wz, T, rho

# --- Simulation thread: writes pure data rows to MPU6050.txt ---
def run_simulation():
    global running
    running = True
    start_wall = time.time()

    # Prepare output file with a strict, parseable header + columns
    with open("MPU6050.txt", "w") as f:
        # Column header only (pure data capture below)
        f.write("time_s,alt_m,temp_C,air_density_kgm3,gyro_x_degs,gyro_y_degs,gyro_z_degs\n")

        # Main loop
        for i in range(int(SIM_DURATION_S * SAMPLE_RATE_HZ)):
            if not running:
                break
            t_s = i / SAMPLE_RATE_HZ
            alt = altitude_profile(t_s)
            wx, wy, wz, T, rho = angular_velocity(t_s, alt)

            # Convert rad/s → deg/s
            gx = math.degrees(wx)
            gy = math.degrees(wy)
            gz = math.degrees(wz)

            # Write row
            line = f"{t_s:.2f},{alt:.2f},{T:.2f},{rho:.5f},{gx:.2f},{gy:.2f},{gz:.2f}\n"
            f.write(line)
            f.flush()

            # Update GUI
            elapsed_var.set(f"{t_s:.2f}")
            altitude_var.set(f"{alt:.2f}")
            temp_var.set(f"{T:.2f}")
            density_var.set(f"{rho:.5f}")
            gyro_x_var.set(f"{gx:.2f}")
            gyro_y_var.set(f"{gy:.2f}")
            gyro_z_var.set(f"{gz:.2f}")

            time.sleep(1.0 / SAMPLE_RATE_HZ)

def start_sim():
    # Reset display
    elapsed_var.set("0.00")
    gyro_x_var.set("0.00")
    gyro_y_var.set("0.00")
    gyro_z_var.set("0.00")
    altitude_var.set("0.00")
    temp_var.set("0.00")
    density_var.set("0.00000")
    threading.Thread(target=run_simulation, daemon=True).start()

def stop_sim():
    global running
    running = False

# --- Tkinter GUI ---
root = tk.Tk()
root.title("HAB Payload MPU6050 Simulation (Altitude & Atmosphere)")

# Mission info
info_frame = ttk.LabelFrame(root, text="Mission info")
info_frame.pack(fill="x", padx=10, pady=6)
for text in [
    f"Date: {MISSION_DATE}",
    f"Start time: {MISSION_START}",
    f"Landing time: {MISSION_LAND}",
    f"Payload dimensions (m): {PAYLOAD_DIMENSIONS}",
    f"Balloon burst altitude (m): {BALLOON_BURST_ALTITUDE}",
    f"Chute deployment: {'FAILED' if not CHUTE_DEPLOYMENT else 'SUCCESS'}"
]:
    ttk.Label(info_frame, text=text).pack(anchor="w")

# Weather config (display only; adjust defaults in code or add inputs)
weather_frame = ttk.LabelFrame(root, text="Weather environment")
weather_frame.pack(fill="x", padx=10, pady=6)
ttk.Label(weather_frame, text=f"Wind speed (m/s): {weather['wind_speed']}").pack(anchor="w")
ttk.Label(weather_frame, text=f"Turbulence (0–1): {weather['turbulence']}").pack(anchor="w")
ttk.Label(weather_frame, text=f"Temperature bias (deg/s per °C): {weather['temperature_bias']}").pack(anchor="w")

# Atmosphere & gyro live data
atm_frame = ttk.LabelFrame(root, text="Atmosphere & live data")
atm_frame.pack(fill="x", padx=10, pady=6)

elapsed_var = tk.StringVar(value="0.00")
altitude_var = tk.StringVar(value="0.00")
temp_var = tk.StringVar(value="0.00")
density_var = tk.StringVar(value="0.00000")
gyro_x_var = tk.StringVar(value="0.00")
gyro_y_var = tk.StringVar(value="0.00")
gyro_z_var = tk.StringVar(value="0.00")

labels = [
    ("Time (s):", elapsed_var),
    ("Altitude (m):", altitude_var),
    ("Temperature (°C):", temp_var),
    ("Air density (kg/m³):", density_var),
    ("Gyro X (deg/s):", gyro_x_var),
    ("Gyro Y (deg/s):", gyro_y_var),
    ("Gyro Z (deg/s):", gyro_z_var),
]
for i, (lab, var) in enumerate(labels):
    ttk.Label(atm_frame, text=lab).grid(row=i, column=0, sticky="w", padx=4, pady=2)
    ttk.Label(atm_frame, textvariable=var).grid(row=i, column=1, sticky="w", padx=4, pady=2)

# Controls
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)
ttk.Button(btn_frame, text="Start simulation", command=start_sim).grid(row=0, column=0, padx=6)
ttk.Button(btn_frame, text="Stop simulation", command=stop_sim).grid(row=0, column=1, padx=6)

root.mainloop()
