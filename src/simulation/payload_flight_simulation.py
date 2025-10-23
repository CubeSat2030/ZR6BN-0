#!/usr/bin/env python3
"""
BACAR-13 Cinematic Payload Flight Replay
- Uses real logger/data/MPU6050.txt (headers as provided)
- Recreates payload rotation from gyro (gyro_x_dps, gyro_y_dps, gyro_z_dps)
- Cinematic 3D left panel + telemetry stack right panel
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial.transform import Rotation as R
from scipy.signal import savgol_filter
import matplotlib.gridspec as gridspec
import warnings

# -------------------------
# CONFIG — edit if required
# -------------------------
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "logger", "data", "MPU6050.txt")
REALTIME_SPEED = 1.0
CUBE_SIZE = 0.12
ACC_SCALE = 0.015
TRAIL_LENGTH = 80
MAX_ALTITUDE_CLIP = 32000.0
SMOOTH_WINDOW = 51   # must be odd; will be reduced if sequence is short
SMOOTH_POLYORDER = 3

# -------------------------
# LOAD DATA (robust)
# -------------------------
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"MPU6050 file not found at: {DATA_FILE}")

# read file (skip comment lines starting with '#')
df = pd.read_csv(DATA_FILE, comment="#")
if "timestamp" not in df.columns:
    raise ValueError("MPU6050.txt must contain a 'timestamp' column")

# Parse timestamps, drop bad rows
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

# Keep only the columns we need (tolerant to extra columns)
expected_cols = [
    "velocity_m_s", "accel_x_m_s2", "accel_y_m_s2", "accel_z_m_s2",
    "gyro_x_dps", "gyro_y_dps", "gyro_z_dps"
]
for c in expected_cols:
    if c not in df.columns:
        # create fallback columns filled with zeros to avoid crashes
        df[c] = 0.0

# Interpolate numeric columns and fill remaining NaNs
df = df.sort_values("timestamp").reset_index(drop=True)
df[df.select_dtypes(include=[np.number]).columns] = df.select_dtypes(include=[np.number]).interpolate().fillna(0.0)

# time arrays
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
dt[dt <= 0] = np.mean(dt[dt > 0]) if np.any(dt > 0) else 1.0

# velocity -> altitude integration (fallback if velocity column zeros)
vel = df["velocity_m_s"].to_numpy(dtype=float)
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i] * dt[i]
alt = np.clip(alt, 0.0, MAX_ALTITUDE_CLIP)

# gyro (dps -> deg/s -> rad/s)
gyro_dps = df[["gyro_x_dps", "gyro_y_dps", "gyro_z_dps"]].to_numpy(dtype=float)
# apply Savitzky-Golay smoothing if long enough
n = len(gyro_dps)
if n >= 7:
    win = SMOOTH_WINDOW if SMOOTH_WINDOW < n else (n // 2) * 2 + 1
    if win < 5:
        win = 5 if n >= 5 else (n if n % 2 == 1 else n-1)
    try:
        gyro_smoothed = np.zeros_like(gyro_dps)
        for i in range(3):
            gyro_smoothed[:, i] = savgol_filter(gyro_dps[:, i], win, SMOOTH_POLYORDER)
    except Exception:
        gyro_smoothed = gyro_dps.copy()
else:
    gyro_smoothed = gyro_dps.copy()

# convert to rad/s for integration (dps -> deg/s -> rad/s)
gyro_rad = np.deg2rad(gyro_smoothed)

# integrate gyro to get orientations (body frame angular rates -> incremental rotations)
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro_rad[i] * dt[i]   # small-angle approx: rotation vector = omega * dt
    # if magnitude is extremely small, R.from_rotvec handles it
    orientations.append(orientations[-1] * R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

# -------------------------
# Geometry / visuals setup
# -------------------------
L = CUBE_SIZE / 2.0
verts = np.array([
    [-L,-L,-L],[ L,-L,-L],[ L, L,-L],[-L, L,-L],
    [-L,-L, L],[ L,-L, L],[ L, L, L],[-L, L, L]
])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],
         [2,3,7,6],[1,2,6,5],[0,3,7,4]]

def altitude_to_color(h):
    if h > 12000:
        t = np.clip(h / 32000.0, 0, 1)
        r = 0.0 + 0.15*(1 - t)
        g = 0.05 + 0.5*(1 - t)
        b = 0.1 + 1.0*(1 - t/2)
    else:
        t = np.clip(h / 12000.0, 0, 1)
        r = 0.5 * (1 - t) + 0.1 * t
        g = 0.7 * (1 - t) + 0.3 * t
        b = 1.0 * (1 - t) + 0.5 * t
        haze = 0.2 * (1 - t)
        r += haze; g += haze * 0.8; b += haze * 0.6
    return (np.clip(r,0,1), np.clip(g,0,1), np.clip(b,0,1))

# Matplotlib figure: left 3D, right telemetry stack
plt.style.use("dark_background")
fig = plt.figure(figsize=(18,10))
gs = gridspec.GridSpec(1,2, width_ratios=[2.0, 1.0], wspace=0.12)

ax3d = fig.add_subplot(gs[0], projection="3d")
ax3d.set_box_aspect((1,1,1))
ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])
ax3d.set_xlim([-L*6, L*6]); ax3d.set_ylim([-L*6, L*6]); ax3d.set_zlim([-L*6, L*6])

# right telemetry axes (stack)
right_gs = gs[1].subgridspec(6,1, hspace=0.35)
ax_accel = fig.add_subplot(right_gs[0])
ax_gyro  = fig.add_subplot(right_gs[1], sharex=ax_accel)
ax_vel   = fig.add_subplot(right_gs[2], sharex=ax_accel)
ax_alt_t = fig.add_subplot(right_gs[3], sharex=ax_accel)
ax_mag   = fig.add_subplot(right_gs[4], sharex=ax_accel)
ax_dummy = fig.add_subplot(right_gs[5], sharex=ax_accel)

for a in (ax_gyro, ax_vel, ax_alt_t, ax_mag, ax_dummy):
    plt.setp(a.get_xticklabels(), visible=False)
    a.grid(True, alpha=0.2)

ax_accel.set_title("BACAR-13 — MPU6050 Telemetry")
ax_accel.set_ylabel("Accel (m/s²)")
ax_gyro.set_ylabel("Gyro (dps)")
ax_vel.set_ylabel("Vel (m/s)")
ax_alt_t.set_ylabel("Alt (m)")
ax_mag.set_ylabel("|a| (m/s²)")

# Build telemetry plots from df
tvals = df["timestamp"]
ax_accel.plot(tvals, df["accel_x_m_s2"], lw=0.6, label="ax")
ax_accel.plot(tvals, df["accel_y_m_s2"], lw=0.6, label="ay")
ax_accel.plot(tvals, df["accel_z_m_s2"], lw=0.6, label="az")
ax_accel.legend(loc="upper right", fontsize="small")

ax_gyro.plot(tvals, df["gyro_x_dps"], lw=0.6, label="gx")
ax_gyro.plot(tvals, df["gyro_y_dps"], lw=0.6, label="gy")
ax_gyro.plot(tvals, df["gyro_z_dps"], lw=0.6, label="gz")
ax_gyro.legend(loc="upper right", fontsize="small")

ax_vel.plot(tvals, df["velocity_m_s"], lw=0.8)
ax_alt_t.plot(tvals, alt, lw=0.8, color="#42A5F5")
mag = np.linalg.norm(df[["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].to_numpy(), axis=1)
ax_mag.plot(tvals, mag, lw=0.8, color="#FFD54F")
ax_dummy.axis("off")

# time marker vertical lines on telemetry
time_markers = []
for a in (ax_accel, ax_gyro, ax_vel, ax_alt_t, ax_mag):
    ln = a.axvline(tvals.iloc[0], color="gold", lw=1.0, alpha=0.9)
    time_markers.append(ln)

# 3D artists
poly = Poly3DCollection([], facecolors=(1.0,0.84,0.4), edgecolors="#2a2a2a", lw=0.6, alpha=0.98)
ax3d.add_collection3d(poly)

# trajectory in 3D (vertical line)
traj_x = np.zeros_like(alt)
traj_y = np.zeros_like(alt)
traj_z = alt / (MAX_ALTITUDE_CLIP / 3.0)  # visual scaling
past_line, = ax3d.plot([], [], [], lw=2.2, alpha=0.6)
future_scat = ax3d.scatter([], [], [], s=26, alpha=0.35)

# trail & acc vector (quiver)
trail_buffer = np.zeros((TRAIL_LENGTH, 3))
trail_collection = Line3DCollection([[[0,0,0],[0,0,0]]], colors=[(0.2,0.6,1.0,0.12)], lw=2)
ax3d.add_collection3d(trail_collection)

horizon_radius = 2.5
theta = np.linspace(-np.pi/1.6, np.pi/1.6, 240)
x_arc = horizon_radius * np.cos(theta)
y_arc = horizon_radius * np.sin(theta)
z_arc = np.zeros_like(x_arc)
horizon_line = ax3d.plot(x_arc, y_arc, z_arc, color=(0.3,0.6,1,0.0), lw=6)[0]

halo_artist = None
impact_frame = -1

def get_poly_basecolor(default=(1.0,0.84,0.4)):
    fc = poly.get_facecolor()
    if len(fc) == 0:
        return np.array(default)
    try:
        return np.array(fc[0][:3])
    except Exception:
        return np.array(default)

def update(frame):
    global halo_artist, impact_frame

    # orientation update
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])

    # acceleration vector (body -> world)
    acc_body = df.loc[frame, ["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].to_numpy(dtype=float)
    acc_world = Rm @ (acc_body * ACC_SCALE)

    # recreate a simple quiver by removing previous (small cost)
    if hasattr(update, "_last_quiver") and getattr(update, "_last_quiver", None) is not None:
        try:
            update._last_quiver.remove()
        except Exception:
            pass
    try:
        update._last_quiver = ax3d.quiver(0,0,0, acc_world[0], acc_world[1], acc_world[2],
                                          color="cyan", linewidth=1.2, arrow_length_ratio=0.18)
    except Exception:
        update._last_quiver = None

    # trail
    trail_buffer[:-1] = trail_buffer[1:]
    trail_buffer[-1] = acc_world
    segments = [[trail_buffer[i], trail_buffer[i+1]] for i in range(TRAIL_LENGTH-1)]
    trail_collection.set_segments(segments)

    # trajectory past/future
    past_mask = np.arange(len(times)) <= frame
    future_mask = np.arange(len(times)) > frame
    past_line.set_data(traj_x[past_mask], traj_y[past_mask])
    past_line.set_3d_properties(traj_z[past_mask])
    future_scat._offsets3d = (traj_x[future_mask], traj_y[future_mask], traj_z[future_mask])

    # background color
    bg = altitude_to_color(alt[frame])
    fig.patch.set_facecolor(bg)
    ax3d.set_facecolor(bg)

    # horizon thickening
    horizon_strength = np.clip((5000.0 - alt[frame]) / 5000.0, 0.0, 1.0)
    horizon_color = (0.3 + 0.3*horizon_strength, 0.6 + 0.2*horizon_strength, 1.0, 0.15 + 0.5*horizon_strength)
    horizon_line.set_color(horizon_color)
    horizon_line.set_linewidth(3.5 + 2.5*horizon_strength)

    # lighting (ambient tint below 10km)
    if alt[frame] < 10000:
        ambient_factor = (10000.0 - alt[frame]) / 10000.0
        base = np.array([1.0, 0.84, 0.4])
        tint = np.array([0.0, 0.03, 0.12]) * ambient_factor
        poly.set_facecolor(tuple(np.clip(base + tint, 0, 1)))
    else:
        poly.set_facecolor((1.0,0.84,0.4))

    # ground bloom
    if alt[frame] < 1000:
        bloom_strength = (1000.0 - alt[frame]) / 1000.0
        base_color = get_poly_basecolor()
        poly.set_facecolor(tuple(np.clip(base_color + bloom_strength * 0.1, 0, 1)))

    # camera stabilization
    smooth_factor = np.clip((500.0 - alt[frame]) / 500.0, 0.0, 1.0)
    elev = 18 + np.sin(frame * 0.02) * (4 * (1 - smooth_factor))
    azim = frame * 0.45 * (1 - 0.02 * smooth_factor) + np.sin(frame * 0.03) * (8 * (1 - smooth_factor))
    ax3d.view_init(elev=elev, azim=azim)

    # volumetric halo
    if halo_artist is not None:
        try:
            halo_artist.remove()
        except Exception:
            pass
    halo_artist = None
    if alt[frame] < 12000:
        glow_strength = np.clip((12000.0 - alt[frame]) / 12000.0, 0.0, 1.0)
        halo_size = 1800.0 * (0.08 + 0.92 * glow_strength)
        halo_alpha = 0.02 + 0.35 * glow_strength
        halo_artist = ax3d.scatter([0], [0], [0], s=halo_size, c=[(1.0,0.84,0.4,halo_alpha)], edgecolors='none')

    # impact flash
    if impact_frame == -1 and alt[frame] <= 5.0:
        impact_frame = frame
    if impact_frame != -1:
        elapsed = (frame - impact_frame) * np.mean(dt)
        if elapsed < 2.0:
            flash_strength = max(0.0, 1.0 - elapsed / 2.0)
            flash_color = (1.0,1.0,1.0)
            blended = tuple(flash_color[i] * flash_strength + bg[i] * (1.0 - flash_strength) for i in range(3))
            fig.patch.set_facecolor(blended)
            ax3d.set_facecolor(blended)

    # telemetry time markers
    current_ts = df["timestamp"].iloc[frame]
    for ln in time_markers:
        ln.set_xdata([current_ts,current_ts])

    # update title / HUD
    fig.suptitle(
        f"BACAR-13 | t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | Vel={vel[frame]:.1f} m/s | |a|={np.linalg.norm(acc_body):.1f} m/s²",
        fontsize=14, color="white", y=0.96
    )

    # return artists (blit disabled in FuncAnimation, but return for completeness)
    artists = [poly, past_line, future_scat, trail_collection] + time_markers
    if hasattr(update, "_last_quiver") and update._last_quiver:
        artists.append(update._last_quiver)
    if halo_artist is not None:
        artists.append(halo_artist)
    return artists

# -------------------------
# RUN
# -------------------------
ani = FuncAnimation(
    fig, update, frames=len(df), interval=np.mean(dt) * 1000.0 / REALTIME_SPEED,
    blit=False, repeat=False
)

plt.tight_layout()
plt.show()

# To export: 
ani.save("BACAR13_replay.mp4", fps=30, dpi=180)
