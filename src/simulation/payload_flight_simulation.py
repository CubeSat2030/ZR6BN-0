#!/usr/bin/env python3
"""
payload_flight_simulation.py
---------------------------------
Integrated cinematic replay (Option A) — split-screen MP4.

Left:  3D cinematic payload (cube + rod), trail (past + future), dynamic atmosphere fade.
Right: Telemetry charts (accel + gyro) that scroll in sync with the animation frames.

Outputs:
    src/simulation/output/BACAR13_flight_replay.mp4
    src/simulation/output/altitude_profile.png
    src/simulation/output/MPU6050.txt

Requirements:
    python >=3.8, packages: numpy, pandas, matplotlib, ffmpeg (system)
Place alongside your other simulation files in src/simulation/.
"""
import os
from pathlib import Path
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D  # registers 3d projection
from datetime import datetime, time

# Paths (relative to file)
HERE = Path(__file__).resolve().parent
# NOTE: Update this path if your MPU6050.txt is located elsewhere
DATA_PATH = HERE.parent / "logger" / "data" / "MPU6050.txt"
OUTPUT_DIR = HERE / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_MP4 = OUTPUT_DIR / "BACAR13_flight_replay.mp4"
OUT_RECON = OUTPUT_DIR / "MPU6050.txt"
OUT_ALT_PLOT = OUTPUT_DIR / "altitude_profile.png"

# Config
NOMINAL_RATE_HZ = 10.0
FPS = 10  # frames per second in MP4
DOTS_PAST = 60   # number of trailing dots to draw behind current time
DOTS_FUTURE = 120  # number of future dots to draw ahead (visual only)
ROD_LENGTH = 10.0  # visual rod length in meters
FIGSIZE = (16, 9)

# Event timestamps (SAST local times). We'll search for matching timestamps in data.
# Format: "HH:MM" (24-hour). User provided 08:36 (launch), 09:18 (burst), 12:15 (landing)
EVENTS = {
    "LAUNCH": "08:36",
    "BURST": "09:18",
    "LANDING": "12:15"
}

# Helper: parse events into datetimes matching data timestamps if possible
def find_event_indices(df):
    idx_map = {}
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        times = ts.dt.time
        for name, hhmm in EVENTS.items():
            hh, mm = [int(x) for x in hhmm.split(":")]
            want = time(hour=hh, minute=mm)
            matches = np.where(times == want)[0]
            if matches.size > 0:
                idx_map[name] = matches[0]
            else:
                secs = ts.dt.hour * 3600 + ts.dt.minute * 60 + ts.dt.second
                want_secs = hh * 3600 + mm * 60
                absdiff = np.abs(secs - want_secs)
                idx = int(absdiff.idxmin()) if len(absdiff)>0 else 0
                idx_map[name] = idx
    else:
        N = len(df)
        idx_map["LAUNCH"] = 0
        idx_map["BURST"] = min(int(N * 0.25), N-1)
        idx_map["LANDING"] = N-1
    return idx_map

# Load enhanced text (skips comment lines starting '#')
def load_enhanced_txt(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Expected file: {path} not found.")
    with open(path, "r") as f:
        lines = f.readlines()
    data_lines = [ln for ln in lines if not ln.lstrip().startswith("#") and ln.strip() != ""]
    if len(data_lines) == 0:
        raise RuntimeError("No data lines found in enhanced txt.")
    df = pd.read_csv(io.StringIO("".join(data_lines)), header=0)
    if "timestamp" in df.columns:
        try:
            # Check if timestamps are already datetime objects before converting
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        except Exception:
            pass
    return df

# Kinematic reconstruction functions
def compute_time_array(df, nominal_rate=NOMINAL_RATE_HZ):
    if "timestamp" in df.columns and df["timestamp"].notna().sum() > 1:
        # Use pandas datetime subtraction for precise time difference
        t = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().to_numpy()
    else:
        # Use nominal rate if timestamps are missing or invalid
        dt = 1.0 / float(nominal_rate)
        t = np.arange(len(df)) * dt
    return t

def compute_vertical_velocity(df, t):
    if "velocity_m_s" in df.columns and df["velocity_m_s"].notna().sum() > 0:
        # Use existing velocity if available
        vz = df["velocity_m_s"].fillna(method="ffill").fillna(0.0).to_numpy()
    elif "linear_accel_z_m_s2" in df.columns:
        # Integrate acceleration (trapezoidal rule)
        a = df["linear_accel_z_m_s2"].fillna(0.0).to_numpy()
        vz = np.zeros_like(a)
        for i in range(1, len(a)):
            dt = t[i] - t[i-1]
            vz[i] = vz[i-1] + 0.5*(a[i] + a[i-1])*dt
    else:
        vz = np.zeros(len(df))
    return vz

def integrate_altitude(vz, t):
    # Integrate velocity (trapezoidal rule) to get altitude
    z = np.zeros_like(vz)
    for i in range(1, len(vz)):
        dt = t[i] - t[i-1]
        z[i] = z[i-1] + 0.5 * (vz[i] + vz[i-1]) * dt
    return z

def integrate_gyro_angles(df, t):
    # Integrate angular rates (Euler integration)
    n = len(df)
    gx = df.get("gyro_x_rads", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    gy = df.get("gyro_y_rads", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    gz = df.get("gyro_z_rads", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    roll = np.zeros(n); pitch = np.zeros(n); yaw = np.zeros(n)
    for i in range(1,n):
        dt = t[i] - t[i-1]
        roll[i]  = roll[i-1]  + gx[i] * dt
        pitch[i] = pitch[i-1] + gy[i] * dt
        yaw[i]   = yaw[i-1]   + gz[i] * dt
    return yaw, pitch, roll

def atmosphere_color(t, cmap_name="plasma"):
    # Create a normalized time array for color mapping (atmosphere fade effect)
    tnorm = (t - t[0]) / max(1e-9, (t[-1] - t[0]))
    cmap = plt.get_cmap(cmap_name)
    return cmap(tnorm)

def draw_static_right_panel_axes(fig):
    # Setup for the telemetry panel (charts)
    right = fig.add_gridspec(5, 2, width_ratios=[1,1], left=0.55, right=0.99, top=0.96, bottom=0.04, hspace=0.6)
    ax_accel = fig.add_subplot(right[0:2, :])
    ax_accel.set_title("Acceleration (m/s²) - X (yellow), Y (green), Z (cyan)")
    ax_accel.set_ylabel("m/s²")
    ax_gyro = fig.add_subplot(right[2:4, :])
    ax_gyro.set_title("Gyroscope (deg/s) - X (red), Y (green), Z (blue)")
    ax_gyro.set_ylabel("deg/s")
    ax_time = fig.add_subplot(right[4, :])
    ax_time.set_title("Timestamp / Phase")
    ax_time.set_yticks([])
    return ax_accel, ax_gyro, ax_time

def create_figure():
    # Setup for the main figure and left 3D panel
    fig = plt.figure(figsize=FIGSIZE)
    left = fig.add_gridspec(1, 1, left=0.02, right=0.53) # 1 column in the left section
    ax3d = fig.add_subplot(left[0, 0], projection="3d")
    ax_accel, ax_gyro, ax_time = draw_static_right_panel_axes(fig)
    return fig, ax3d, ax_accel, ax_gyro, ax_time

def make_animation(df, t, z, yaw, pitch, roll, event_indices, out_path=OUT_MP4, fps=FPS):
    n = len(t)
    colors = atmosphere_color(t)
    axx = df.get("accel_x_m_s2", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    axy = df.get("accel_y_m_s2", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    axz = df.get("accel_z_m_s2", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    gxd = df.get("gyro_x_dps", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    gyd = df.get("gyro_y_dps", pd.Series(np.zeros(n))).fillna(0).to_numpy()
    gzd = df.get("gyro_z_dps", pd.Series(np.zeros(n))).fillna(0).to_numpy()

    fig, ax3d, ax_accel, ax_gyro, ax_time = create_figure()

    # 3D Setup
    ax3d.set_xlim(-100, 100); ax3d.set_ylim(-100, 100)
    ax3d.set_zlim(np.min(z)-50, np.max(z)+50)
    ax3d.set_xlabel("X (m)"); ax3d.set_ylabel("Y (m)"); ax3d.set_zlabel("Altitude (m)")

    # Initialize persistent 3D artists (scatter points are drawn dynamically)
    past_scatter = ax3d.scatter([], [], [], s=15, c="white", alpha=0.6)
    future_scatter = ax3d.scatter([], [], [], s=6, c="lightgrey", alpha=0.4)
    # Persistent rod and cube artists that will be updated using set_data
    rod_line, = ax3d.plot([], [], [], lw=6, color="#b0b8c6")
    cube_marker, = ax3d.plot([], [], [], marker="s", markersize=20, linestyle="None", color="#d9c9ff")

    # 2D Chart Setup
    t_sec = t
    accel_line_x, = ax_accel.plot(t_sec, axx, lw=0.5, color="#ffee58", label="Accel X")
    accel_line_y, = ax_accel.plot(t_sec, axy, lw=0.5, color="#66bb6a", label="Accel Y")
    accel_line_z, = ax_accel.plot(t_sec, axz, lw=0.5, color="#4dd0e1", label="Accel Z")
    ax_accel.legend(loc="upper right", fontsize="small")
    gyro_line_x, = ax_gyro.plot(t_sec, gxd, lw=0.5, color="#ef5350", label="Gyro X")
    gyro_line_y, = ax_gyro.plot(t_sec, gyd, lw=0.5, color="#66bb6a", label="Gyro Y")
    gyro_line_z, = ax_gyro.plot(t_sec, gzd, lw=0.5, color="#42a5f5", label="Gyro Z")
    ax_gyro.legend(loc="upper right", fontsize="small")

    # Time/Event Markers
    vline_accel = ax_accel.axvline(x=0.0, color="white", linewidth=1.2)
    vline_gyro  = ax_gyro.axvline(x=0.0, color="white", linewidth=1.2)
    time_text = ax_time.text(0.02, 0.5, "", transform=ax_time.transAxes, color="white", fontsize=12)

    event_texts = {}
    for name, idx in event_indices.items():
        event_texts[name] = ax3d.text2D(0.02, 0.95 - 0.04*len(event_texts), "", transform=ax3d.transAxes, color="white", fontsize=12)

    # Styling (Dark Theme)
    fig.patch.set_facecolor("#000000")
    for ax in [ax_accel, ax_gyro, ax_time]:
        ax.set_facecolor("#111111")
        for spine in ax.spines.values():
            spine.set_color("#444444")
        ax.tick_params(colors="#cccccc", which="both")
        ax.xaxis.label.set_color("#cccccc")
        ax.yaxis.label.set_color("#cccccc")
        ax.title.set_color("#f0f0f0")
    ax_time.set_xlim(t_sec[0], t_sec[-1])
    ax_accel.set_xlim(t_sec[0], t_sec[-1])
    ax_gyro.set_xlim(t_sec[0], t_sec[-1])
    
    # 3D Axis background (pane) color is set inside update for dynamic fade

    def update(i):
        # Dynamic atmosphere/pane color based on time/altitude
        col = colors[i]
        ax3d.xaxis.set_pane_color((col[0]*0.05, col[1]*0.05, col[2]*0.05, 1.0))
        ax3d.yaxis.set_pane_color((col[0]*0.05, col[1]*0.05, col[2]*0.05, 1.0))
        ax3d.zaxis.set_pane_color((col[0]*0.07, col[1]*0.07, col[2]*0.07, 1.0))

        # Trail data indexing
        start_past = max(0, i - DOTS_PAST)
        past_idx = np.arange(start_past, i+1)
        future_idx = np.arange(i, min(n, i + DOTS_FUTURE))
        xs_p = np.zeros_like(past_idx, dtype=float)
        ys_p = np.zeros_like(past_idx, dtype=float)
        zs_p = z[past_idx]
        xs_f = np.zeros_like(future_idx, dtype=float)
        ys_f = np.zeros_like(future_idx, dtype=float)
        zs_f = z[future_idx]

        # --- FIX 1: ATTRIBUTEERROR ---
        # Remove all dynamically created scatter collections from the previous frame.
        for collection in ax3d.collections[:]:
            collection.remove()
        # --- END FIX 1 ---
        
        # Redraw scatter plots (past trail and future path)
        ax3d.scatter(xs_p, ys_p, zs_p, s=20, c=colors[past_idx], alpha=0.9, depthshade=True)
        ax3d.scatter(xs_f, ys_f, zs_f, s=6, c=colors[future_idx], alpha=0.35, depthshade=False)

        # Update rod and cube position/orientation
        roll_i = roll[i]; pitch_i = pitch[i]
        # Simplistic 2D rotation projection for visualization purposes:
        dx = np.sin(roll_i) * ROD_LENGTH / 2.0
        dy = np.sin(pitch_i) * ROD_LENGTH / 2.0
        x_points = np.array([-dx, dx])
        y_points = np.array([-dy, dy])
        z_points = np.array([z[i] - ROD_LENGTH/2.0, z[i] + ROD_LENGTH/2.0])
        
        # --- FIX 2: 'x must be a sequence' ERROR ---
        # The correct way to update a 3D line artist is using set_data_3d.
        rod_line.set_data_3d(x_points, y_points, z_points)
        
        # Cube marker update (single point)
        cube_marker.set_data([0.0], [0.0])
        cube_marker.set_3d_properties([z[i]])
        # --- END FIX 2 ---

        # Update 2D chart elements (vertical line) and text
        curt = t_sec[i]
        vline_accel.set_xdata(curt)
        vline_gyro.set_xdata(curt)
        
        # Adjust X-axis limits for scrolling effect
        window_size = 30.0 # Time window to display in the charts (30 seconds)
        center = curt
        ax_accel.set_xlim(max(t_sec[0], center - window_size/2), min(t_sec[-1], center + window_size/2))
        ax_gyro.set_xlim(max(t_sec[0], center - window_size/2), min(t_sec[-1], center + window_size/2))

        # Update time/event text
        time_str = f"t = {curt:.1f} s"
        if "timestamp" in df.columns:
            ts = df['timestamp'].iloc[i]
            # Format the datetime object nicely if it's not NaT
            if not pd.isna(ts) and isinstance(ts, pd.Timestamp):
                time_str += f" | {ts.strftime('%H:%M:%S.%f')[:-3]}" # remove last 3 microseconds
        time_text.set_text(time_str)

        # Update event markers
        for name, idx in event_indices.items():
            txt_obj = event_texts[name]
            window_s = 3.0
            if i >= idx - int(window_s*FPS) and i <= idx + int(window_s*FPS):
                txt_obj.set_text(f"{name} (t={t[idx]:.1f}s)")
            else:
                txt_obj.set_text("")

        # Since blit is False, we can return empty.
        return []

    frames = n
    interval = 1000.0 / fps # interval in ms
    # Note: blit=False is used because 3D plots do not support blitting easily
    anim = animation.FuncAnimation(fig, update, frames=frames, interval=interval, blit=False)

    print(f"[+] Rendering MP4 to: {out_path}  (this may take a while for long datasets)")
    # Using 'ffmpeg' writer, ensure ffmpeg is installed on your system
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps, metadata=dict(artist='BACAR'), bitrate=6000) 
    
    try:
        anim.save(str(out_path), writer=writer)
        print("[✓] MP4 render complete.")
    except Exception as save_e:
        print(f"[!] FFMPEG failed to save the animation. Check if 'ffmpeg' is installed and in your system PATH. Error: {save_e}")
    
    plt.close(fig)

def main():
    print("[...] Loading enhanced MPU6050 data")
    try:
        df = load_enhanced_txt(DATA_PATH)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[FATAL] Error loading data: {e}")
        return

    print("[...] Running kinematic reconstruction")
    t = compute_time_array(df, nominal_rate=NOMINAL_RATE_HZ)
    vz = compute_vertical_velocity(df, t)
    z = integrate_altitude(vz, t)
    yaw, pitch, roll = integrate_gyro_angles(df, t)

    # Save reconstructed data
    out_df = df.copy()
    out_df["recon_time_s"] = t
    out_df["recon_velocity_m_s"] = vz
    out_df["recon_altitude_m"] = z
    out_df.to_csv(OUT_RECON, index=False)
    print(f"[✓] Saved reconstructed file: {OUT_RECON}")

    # Plot altitude profile
    try:
        plt.figure(figsize=(10,4))
        plt.plot(t, z, linewidth=0.9)
        plt.xlabel("Time (s)"); plt.ylabel("Altitude (m)")
        plt.title("Reconstructed Altitude — Kinematic Replay")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(OUT_ALT_PLOT)
        plt.close()
        print(f"[✓] Saved altitude profile: {OUT_ALT_PLOT}")
    except Exception as e:
        print("[!] Could not save altitude plot:", e)

    # Find event indices
    event_idx = find_event_indices(df)

    # Make the animation
    try:
        make_animation(df, t, z, yaw, pitch, roll, event_idx, out_path=OUT_MP4, fps=FPS)
    except Exception as e:
        print(f"[!] Animation rendering failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()