#!/usr/bin/env python3
"""
BACAR-13 Cinematic Payload Flight Simulation
- Left: 3D cinematic payload visualization (past/future trajectory, atmosphere transitions)
- Right: Telemetry chart stack driven from the actual logger/data/MPU6050.txt file
Author:  Nathan Graham Busse
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial.transform import Rotation as R
import matplotlib.gridspec as gridspec
import warnings

# ------------------------------------------------------------------
# CONFIGURATION — Edit these paths as required
# ------------------------------------------------------------------
DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "logger", "data", "MPU6050.txt"
)  # path to your flight log
REALTIME_SPEED = 1.0
CUBE_SIZE = 0.12
ACC_SCALE = 0.015
TRAIL_LENGTH = 80
START_TIME = None  # e.g. "2025-10-11 08:00:00.000" or None to use whole file
END_TIME = None
MAX_ALTITUDE_CLIP = 32000.0

# ------------------------------------------------------------------
# LOAD & PREP DATA (robust)
# ------------------------------------------------------------------
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"MPU6050 file not found at: {DATA_FILE}")

# read with flexible parsing; skip comments starting '#'
df = pd.read_csv(DATA_FILE, comment="#")
if "timestamp" not in df.columns:
    raise ValueError("MPU6050.txt must contain 'timestamp' column")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

# optionally trim to START_TIME / END_TIME
if START_TIME:
    df = df[df["timestamp"] >= pd.to_datetime(START_TIME)]
if END_TIME:
    df = df[df["timestamp"] <= pd.to_datetime(END_TIME)]

# Fill / interpolate missing numeric columns
df = df.interpolate().fillna(0).sort_values(by="timestamp").reset_index(drop=True)

# ensure essential columns exist (UPDATED COLUMN NAMES)
for c in ("gyro_x_rads", "gyro_y_rads", "gyro_z_rads",
          "accel_x_m_s2", "accel_y_m_s2", "accel_z_m_s2"):
    if c not in df.columns:
        raise ValueError(f"Required column '{c}' missing from MPU6050.txt")

# optional velocity column
if "velocity_m_s" not in df.columns:
    # try to integrate accel z (rough): not ideal, but fallback to zero if absent
    df["velocity_m_s"] = 0.0

# times in seconds since start
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
# Gyro is now in rad/s, so we remove the pi/180 conversion.
gyro = df[["gyro_x_rads", "gyro_y_rads", "gyro_z_rads"]].to_numpy()
accel = df[["accel_x_m_s2", "accel_y_m_s2", "accel_z_m_s2"]].to_numpy()
vel = df["velocity_m_s"].to_numpy()

# integrate altitude from velocity (fallback if you have explicit altitude)
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i] * dt[i]
alt = np.clip(alt, 0, MAX_ALTITUDE_CLIP)

# ------------------------------------------------------------------
# ORIENTATION (integrate gyro -> rotation matrices)
# ------------------------------------------------------------------
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro[i] * dt[i]
    orientations.append(orientations[-1] * R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

# ------------------------------------------------------------------
# PAYLOAD GEOMETRY (cube)
# ------------------------------------------------------------------
L = CUBE_SIZE / 2.0
verts = np.array([
    [-L, -L, -L], [ L, -L, -L], [ L,  L, -L], [-L,  L, -L],
    [-L, -L,  L], [ L, -L,  L], [ L,  L,  L], [-L,  L,  L]
])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],
         [2,3,7,6],[1,2,6,5],[0,3,7,4]]

# ------------------------------------------------------------------
# HELPER: altitude -> sky color (space -> strato -> tropo -> ground)
# ------------------------------------------------------------------
def altitude_to_color(h):
    """Return RGB tuple for background color based on altitude (m)."""
    # normalize typical flight envelope
    if h > 12000:  # stratosphere / space fade
        t = np.clip(h / 32000.0, 0, 1)
        r = 0.0 + 0.15*(1 - t)
        g = 0.05 + 0.5*(1 - t)
        b = 0.1 + 1.0*(1 - t/2)
    else:  # troposphere — brighter, hazy
        t = np.clip(h / 12000.0, 0, 1)
        r = 0.5 * (1 - t) + 0.1 * t
        g = 0.7 * (1 - t) + 0.3 * t
        b = 1.0 * (1 - t) + 0.5 * t
        haze = 0.2 * (1 - t)
        r += haze
        g += haze * 0.8
        b += haze * 0.6
    return (np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1))

# ------------------------------------------------------------------
# BUILD FIGURE: left 3D scene + right telemetry grid
# ------------------------------------------------------------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(18, 10))
gs = gridspec.GridSpec(1, 2, width_ratios=[2.0, 1.0], wspace=0.12)

# Left: big 3D scene (payload)
ax3d = fig.add_subplot(gs[0], projection="3d")
ax3d.set_box_aspect((1,1,1))
ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])
ax3d.set_xlim([-L*5, L*5]); ax3d.set_ylim([-L*5, L*5]); ax3d.set_zlim([-L*5, L*5])

# Right: telemetry grid (we will create multiple stacked axes)
right_gs = gs[1].subgridspec(6, 1, hspace=0.35)
ax_accel = fig.add_subplot(right_gs[0])
ax_gyro  = fig.add_subplot(right_gs[1], sharex=ax_accel)
ax_vel   = fig.add_subplot(right_gs[2], sharex=ax_accel)
ax_alt_t = fig.add_subplot(right_gs[3], sharex=ax_accel)
ax_mag   = fig.add_subplot(right_gs[4], sharex=ax_accel)
ax_dummy = fig.add_subplot(right_gs[5], sharex=ax_accel)  # placeholder or extra panel

# tidy up the small axes visually
for a in (ax_gyro, ax_vel, ax_alt_t, ax_mag, ax_dummy):
    plt.setp(a.get_xticklabels(), visible=False)
    a.grid(True, alpha=0.2)

ax_accel.set_title("BACAR-13 — MPU6050 Telemetry (synced)")
ax_accel.grid(True, alpha=0.25)
ax_accel.set_ylabel("Accel (m/s²)")
# UPDATED label
ax_gyro.set_ylabel("Gyro (rad/s)")
ax_vel.set_ylabel("Vel (m/s)")
ax_alt_t.set_ylabel("Alt (m)")
ax_mag.set_ylabel("|a| (m/s²)")

# ------------------------------------------------------------------
# Try to import user's mpu6050_plotter.create_mpu6050_chart if available.
# If present and accepts an ax list or fig to plot into, use it.
# Otherwise we will plot telemetry below using the df directly.
# ------------------------------------------------------------------
try:
    from src.plotter.mpu6050_plotter import create_mpu6050_chart
    _HAS_PLOTTER = True
except Exception:
    _HAS_PLOTTER = False

if _HAS_PLOTTER:
    try:
        # try to let their function draw into our axes if it accepts an axes kw
        # We don't pass file paths — pass the dataframe and our axes
        # NOTE: If create_mpu6050_chart relies on specific old column names, it may fail here.
        create_mpu6050_chart(df, axes=[ax_accel, ax_gyro, ax_vel, ax_alt_t, ax_mag, ax_dummy])
        _PLOTTER_USED = True
    except TypeError:
        # fallback: they may expect only df and return a fig; replot into their fig and then copy lines
        try:
            user_fig = create_mpu6050_chart(df)
            # if user_fig returned a figure, we will replot individually below
            plt.close(user_fig)
            _PLOTTER_USED = False
        except Exception:
            _PLOTTER_USED = False
else:
    _PLOTTER_USED = False

# If we didn't use their plotter, create clean telemetry plots here.
if not _PLOTTER_USED:
    # Accel (x,y,z)
    ax_accel.plot(df["timestamp"], df["accel_x_m_s2"], label="ax", lw=0.7)
    ax_accel.plot(df["timestamp"], df["accel_y_m_s2"], label="ay", lw=0.7)
    ax_accel.plot(df["timestamp"], df["accel_z_m_s2"], label="az", lw=0.7)
    ax_accel.legend(loc="upper right", fontsize="small")

    # Gyro (x,y,z) - UPDATED COLUMN NAMES
    ax_gyro.plot(df["timestamp"], df["gyro_x_rads"], label="gx", lw=0.7)
    ax_gyro.plot(df["timestamp"], df["gyro_y_rads"], label="gy", lw=0.7)
    ax_gyro.plot(df["timestamp"], df["gyro_z_rads"], label="gz", lw=0.7)
    ax_gyro.legend(loc="upper right", fontsize="small")

    # Velocity - UPDATED COLUMN NAME
    ax_vel.plot(df["timestamp"], df["velocity_m_s"], label="vel", lw=0.8)
    ax_vel.legend(loc="upper right", fontsize="small")

    # Altitude
    ax_alt_t.plot(df["timestamp"], alt, label="alt", lw=0.8, color="#42A5F5")
    ax_alt_t.legend(loc="upper right", fontsize="small")

    # Accel magnitude - UPDATED COLUMN NAMES
    mag = np.linalg.norm(df[["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].to_numpy(), axis=1)
    ax_mag.plot(df["timestamp"], mag, label="|a|", lw=0.8, color="#FFD54F")
    ax_mag.legend(loc="upper right", fontsize="small")

    ax_dummy.axis("off")

# Add a vertical time marker line on the telemetry stack (one per axis)
time_markers = []
for a in (ax_accel, ax_gyro, ax_vel, ax_alt_t, ax_mag):
    ln = a.axvline(df["timestamp"].iloc[0], color="gold", lw=1.0, alpha=0.9)
    time_markers.append(ln)

# ------------------------------------------------------------------
# 3D Scene initial artists
# ------------------------------------------------------------------
# payload cube (Poly3DCollection)
poly = Poly3DCollection([], facecolors=(1.0, 0.84, 0.4), edgecolors="#2a2a2a", lw=0.6, alpha=0.98)
ax3d.add_collection3d(poly)

# past and future trajectory lines (z = altitude scaled)
traj_x = np.zeros_like(alt)                # purely vertical line in this visual (x,y = 0)
traj_y = np.zeros_like(alt)
traj_z = alt / (MAX_ALTITUDE_CLIP / 3.0)  # scale to visible arc (arbitrary scaling)
# Past as solid line
past_line, = ax3d.plot([], [], [], lw=2.2, alpha=0.6, solid_capstyle="round")
# Future dotted as faint points
future_scat = ax3d.scatter([], [], [], s=26, alpha=0.35)

# Acceleration vector arrow (quiver-like)
acc_quiver = ax3d.quiver(0,0,0, 0,0,0, color="cyan", linewidth=1.2, arrow_length_ratio=0.2)

# trail buffer for small accelerations visual
trail_buffer = np.zeros((TRAIL_LENGTH, 3))
trail_collection = Line3DCollection([[[0,0,0],[0,0,0]]], colors=[(0.2,0.8,1.0,0.12)], lw=2)
ax3d.add_collection3d(trail_collection)
trail_collection.set_segments([])

# horizon arc (flat ring)
horizon_radius = 2.5
theta = np.linspace(-np.pi/1.6, np.pi/1.6, 240)
x_arc = horizon_radius * np.cos(theta)
y_arc = horizon_radius * np.sin(theta)
z_arc = np.zeros_like(x_arc)
horizon_line = ax3d.plot(x_arc, y_arc, z_arc, color=(0.3,0.6,1,0.0), lw=6)[0]

# Keep one halo handle so we can remove and update it each frame
halo_artist = None

# ------------------------------------------------------------------
# UTILS: safe facecolor read and update
# ------------------------------------------------------------------
def get_poly_basecolor(default=(1.0, 0.84, 0.4)):
    fc = poly.get_facecolor()
    if len(fc) == 0:
        return np.array(default)
    try:
        return np.array(fc[0][:3])
    except Exception:
        return np.array(default)

# ------------------------------------------------------------------
# ANIMATION UPDATE — single frame drives both panels
# ------------------------------------------------------------------
impact_frame = -1
def update(frame):
    global halo_artist, impact_frame

    # rotation & cube
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])

    # acceleration in body -> world (scaled)
    acc_body = accel[frame]
    acc_world = Rm @ (acc_body * ACC_SCALE)
    # update quiver: replace by re-creating (mpl quiver in 3D lacks set_UVC) — remove previous and add new
    # simpler: set segments for a line object (we keep acc_quiver but cannot easily update; remove + redraw)
    try:
        # remove previous quiver if exists (matplotlib's quiver returns Poly3DCollection)
        if hasattr(update, "_last_quiver") and update._last_quiver:
            try:
                update._last_quiver.remove()
            except Exception:
                pass
        update._last_quiver = ax3d.quiver(0,0,0, acc_world[0], acc_world[1], acc_world[2],
                                          color="cyan", linewidth=1.2, arrow_length_ratio=0.18)
    except Exception:
        pass

    # trail buffer update
    trail_buffer[:-1] = trail_buffer[1:]
    trail_buffer[-1] = acc_world
    segments = [[trail_buffer[i], trail_buffer[i+1]] for i in range(TRAIL_LENGTH-1)]
    trail_collection.set_segments(segments)
    # colored fade for trail (not per-segment in 3D easily, keep uniform)
    trail_collection.set_color((0.2, 0.6, 1.0, 0.08 + 0.75*(np.linalg.norm(acc_world)/(np.linalg.norm(accel, axis=1).max()+1e-6))))

    # update past & future trajectory
    past_mask = np.arange(len(times)) <= frame
    future_mask = np.arange(len(times)) > frame
    past_line.set_data(traj_x[past_mask], traj_y[past_mask])
    past_line.set_3d_properties(traj_z[past_mask])
    future_scat._offsets3d = (traj_x[future_mask], traj_y[future_mask], traj_z[future_mask])

    # sky color & background
    bg = altitude_to_color(alt[frame])
    fig.patch.set_facecolor(bg)
    ax3d.set_facecolor(bg)

    # horizon thickening & aerosol below ~5 km
    horizon_strength = np.clip((5000.0 - alt[frame]) / 5000.0, 0.0, 1.0)
    horizon_color = (0.3 + 0.3*horizon_strength, 0.6 + 0.2*horizon_strength, 1.0, 0.15 + 0.5*horizon_strength)
    horizon_line.set_color(horizon_color)
    horizon_line.set_linewidth(3.5 + 2.5*horizon_strength)

    # lighting response on payload (ambient blue tint increase below 10 km)
    if alt[frame] < 10000:
        ambient_factor = (10000.0 - alt[frame]) / 10000.0
        base = np.array([1.0, 0.84, 0.4])
        # shift slightly towards blue
        tint = np.array([0.0, 0.03, 0.12]) * ambient_factor
        poly.set_facecolor(tuple(np.clip(base + tint, 0, 1)))
    else:
        poly.set_facecolor((1.0, 0.84, 0.4))

    # safe ground bloom near surface (<1km)
    if alt[frame] < 1000:
        bloom_strength = (1000.0 - alt[frame]) / 1000.0
        base_color = get_poly_basecolor()
        poly.set_facecolor(tuple(np.clip(base_color + bloom_strength*0.1, 0, 1)))

    # camera stabilization: damp jitter near landing
    smooth_factor = np.clip((500.0 - alt[frame]) / 500.0, 0.0, 1.0)
    elev = 18 + np.sin(frame * 0.02) * (4 * (1 - smooth_factor))
    azim = frame * 0.45 * (1 - 0.02 * smooth_factor) + np.sin(frame * 0.03) * (8 * (1 - smooth_factor))
    ax3d.view_init(elev=elev, azim=azim)

    # volumetric halo/haze around payload (remove previous halo to avoid builds)
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
        # scatter a single translucent point as halo
        halo_artist = ax3d.scatter([0], [0], [0], s=halo_size, c=[(1.0, 0.84, 0.4, halo_alpha)], edgecolors='none')

    # Impact flash handling (if you want a single-frame brightening)
    if impact_frame == -1 and alt[frame] <= 5.0:
        impact_frame = frame
    if impact_frame != -1:
        elapsed = (frame - impact_frame) * np.mean(dt)
        if elapsed < 2.0:
            flash_strength = max(0.0, 1.0 - elapsed / 2.0)
            flash_color = (1.0, 1.0, 1.0)
            blended = tuple(flash_color[i] * flash_strength + bg[i] * (1.0 - flash_strength) for i in range(3))
            fig.patch.set_facecolor(blended)
            ax3d.set_facecolor(blended)

    # update telemetry time markers on right-hand charts
    current_ts = df["timestamp"].iloc[frame]
    for ln in time_markers:
        ln.set_xdata([current_ts, current_ts])

    # update axis titles / HUD
    ax_accel.set_xlim(df["timestamp"].iloc[0], df["timestamp"].iloc[-1])
    fig.suptitle(
        f"BACAR-13 — t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | Vel={vel[frame]:.1f} m/s | |a|={np.linalg.norm(acc_body):.1f} m/s²",
        fontsize=14, color="white", y=0.96
    )

    # return artists for blitting compatibility (we use blit=False so it's fine)
    artists = [poly, past_line, future_scat, trail_collection]
    if hasattr(update, "_last_quiver") and update._last_quiver:
        artists.append(update._last_quiver)
    if halo_artist is not None:
        artists.append(halo_artist)
    artists.extend(time_markers)
    return artists

# ------------------------------------------------------------------
# RUN animation
# ------------------------------------------------------------------
ani = FuncAnimation(
    fig, update, frames=len(df), interval=np.mean(dt) * 1000.0 / REALTIME_SPEED,
    blit=False, repeat=False
)

plt.tight_layout()
plt.show()

# To export:
ani.save("BACAR13_cinematic_replay.mp4", fps=30, dpi=200)