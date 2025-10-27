#!/usr/bin/env python3
"""
payload_flight_simulation.py
-------------------------------------------------------
Cinematic, physics-accurate payload flight animation
with realistic troposphere transition.

Compatible with:
  • Matplotlib 3.10.3
  • SciPy 1.16.0
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation as R

# -----------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------
DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "logger", "data", "MPU6050.txt"
)
REALTIME_SPEED = 1.0
CUBE_SIZE = 0.1
ACC_SCALE = 0.015
TRAIL_LENGTH = 60
START_TIME = "2025-10-11 08:00:00.000"
END_TIME   = "2025-10-11 11:00:00.000"

STRATOPAUSE   = 12000.0   # above: stratosphere
MID_TROPO     = 5000.0
NEAR_SURFACE  = 1000.0

# -----------------------------------------------------------------
# LOAD & PREPARE DATA (auto-handle missing timestamp)
# -----------------------------------------------------------------
df = pd.read_csv(DATA_FILE, comment="#")
df.columns = [c.strip().lower() for c in df.columns]

if any(c in df.columns for c in ["timestamp", "time", "datetime"]):
    col = next(c for c in df.columns if c in ["timestamp", "time", "datetime"])
    df["timestamp"] = pd.to_datetime(df[col], errors="coerce")
else:
    print("⚠️ No timestamp column found — generating synthetic timestamps at 10 Hz.")
    start_time = pd.Timestamp(START_TIME)
    freq_hz = 10.0
    df["timestamp"] = [start_time + pd.Timedelta(seconds=i / freq_hz)
                       for i in range(len(df))]

df = df[(df["timestamp"] >= START_TIME) & (df["timestamp"] <= END_TIME)]
df = df.interpolate().fillna(0).sort_values("timestamp").reset_index(drop=True)

times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])

gyro = df[[c for c in df.columns if "gyro" in c]].to_numpy() * np.pi / 180.0
accel = df[[c for c in df.columns if "accel" in c]].to_numpy()
vel = df["velocity_m_s"].to_numpy() if "velocity_m_s" in df else np.zeros(len(df))

# -----------------------------------------------------------------
# INTEGRATE ALTITUDE
# -----------------------------------------------------------------
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i]*dt[i]
alt = np.clip(alt, 0, 32000)

# -----------------------------------------------------------------
# ORIENTATION INTEGRATION (safe for SciPy 1.16.0)
# -----------------------------------------------------------------
orientations = [R.identity()]

for i in range(1, len(df)):
    omega = np.array(gyro[i], dtype=float).reshape(-1)
    if omega.size != 3 or not np.all(np.isfinite(omega)):
        omega = np.zeros(3)
    omega = omega * dt[i]
    try:
        dR = R.from_rotvec(omega)
    except ValueError:
        dR = R.identity()
    orientations.append(orientations[-1] * dR)

rotations = np.array([r.as_matrix() for r in orientations])

# -----------------------------------------------------------------
# PAYLOAD GEOMETRY (define L, verts, faces)
# -----------------------------------------------------------------
L = CUBE_SIZE / 2
verts = np.array([
    [-L, -L, -L], [+L, -L, -L], [+L, +L, -L], [-L, +L, -L],
    [-L, -L, +L], [+L, -L, +L], [+L, +L, +L], [-L, +L, +L]
])
faces = [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [0, 1, 5, 4],
    [2, 3, 7, 6],
    [1, 2, 6, 5],
    [0, 3, 7, 4],
]

# -----------------------------------------------------------------
# FIGURE SETUP
# -----------------------------------------------------------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(14,7))
gs = fig.add_gridspec(2,2,width_ratios=[1.05,1.4])
ax_alt = fig.add_subplot(gs[0,0])
ax_vel = fig.add_subplot(gs[1,0])
ax3d   = fig.add_subplot(gs[:,1], projection="3d")

for a in (ax_alt, ax_vel):
    a.grid(True, alpha=0.25)
    a.set_facecolor("#000010")

ax_alt.set_title("Altitude profile")
ax_alt.set_ylabel("Altitude (m)")
ax_vel.set_title("Vertical velocity")
ax_vel.set_ylabel("Velocity (m/s)")
ax_vel.set_xlabel("Time (s)")

ax3d.set_xlim([-L*4,L*4]); ax3d.set_ylim([-L*4,L*4]); ax3d.set_zlim([-L*4,L*4])
ax3d.set_xlabel("X (m)"); ax3d.set_ylabel("Y (m)"); ax3d.set_zlabel("Z (m)")
ax3d.set_facecolor("#000000")

# -----------------------------------------------------------------
# (rest of your script remains unchanged)
# -----------------------------------------------------------------

# Stars
np.random.seed(42)
star_pos = np.random.uniform(-3,3,(120,3))
star_sizes = np.random.uniform(2,5,120)
star_alphas = np.random.uniform(0.02,0.08,120)
star_scat = ax3d.scatter(star_pos[:,0], star_pos[:,1], star_pos[:,2],
                         color=[(1,1,1,a) for a in star_alphas],
                         s=star_sizes, depthshade=False)

# Telemetry lines
alt_line, = ax_alt.plot(times, alt, color="#42A5F5", lw=1)
vel_line, = ax_vel.plot(times, vel, color="#EF5350", lw=1)
alt_marker, = ax_alt.plot([], [], "o", color="gold")
vel_marker, = ax_vel.plot([], [], "o", color="gold")

# Cube
cube_facecolor = np.array([1.0,0.84,0.33])
poly = Poly3DCollection([], facecolors=[cube_facecolor],
                        edgecolors="#333333", lw=0.4, alpha=0.95)
ax3d.add_collection3d(poly)

# Trail
dummy_segments = np.array([[[0,0,0],[0,0,0]]])
trail_segments = Line3DCollection(dummy_segments,
                                  colors=[(0.4,0.8,1.0,0.2)], lw=2)
ax3d.add_collection3d(trail_segments)
trail_segments.set_segments([])

fig.suptitle("ZR6BN Payload Flight — Cinematic (Troposphere Transition)",
             fontsize=14, color="white")

# -----------------------------------------------------------------
# ENVIRONMENT PROFILE
# -----------------------------------------------------------------
def environment_color_profile(h):
    t_s = np.clip((h-STRATOPAUSE)/(32000-STRATOPAUSE),0,1)
    sky_space = np.array([0.01,0.02,0.06])
    sky_tropo = np.array([0.72,0.9,0.98])
    sky_mix = t_s*sky_space + (1-t_s)*sky_tropo

    horizon_base = np.array([0.5,0.78,1.0])
    horizon_alpha = np.clip((8000-h)/8000,0.0,0.95)
    horizon_rgba = (*horizon_base, 0.05+0.95*horizon_alpha)

    if h> MID_TROPO: haze = 0.0
    elif h> NEAR_SURFACE: haze = np.clip((MID_TROPO-h)/(MID_TROPO-NEAR_SURFACE),0.0,0.7)
    else: haze = 0.9

    star_scale = np.clip((h-MID_TROPO)/(32000-MID_TROPO),0.0,1.0)
    tint_strength = np.clip((MID_TROPO-h)/MID_TROPO,0.0,0.6)
    payload_tint = np.array([0.35,0.55,0.95])*tint_strength

    return tuple(sky_mix), horizon_rgba, haze, star_scale, tuple(payload_tint), tint_strength

# -----------------------------------------------------------------
# STATE
# -----------------------------------------------------------------
trail_buffer = np.zeros((TRAIL_LENGTH,3))
impact_frame = -1
star_base_colors = [(1,1,1,a) for a in star_alphas]

# Horizon arc
horizon_radius = 2.5
theta = np.linspace(-np.pi/1.5, np.pi/1.5, 300)
x_arc = horizon_radius*np.cos(theta)
y_arc = horizon_radius*np.sin(theta)
z_arc = np.zeros_like(x_arc)-0.2
horizon_line, = ax3d.plot(x_arc,y_arc,z_arc,color=(0.3,0.6,1.0,0.0),lw=6,zorder=0)

# -----------------------------------------------------------------
# UPDATE FUNCTION
# -----------------------------------------------------------------
def update(frame):
    global impact_frame
    Rm = rotations[frame]
    rotated = (Rm@verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])

    acc_body = accel[frame]
    acc_world = Rm@(acc_body*ACC_SCALE)

    trail_buffer[:-1] = trail_buffer[1:]
    trail_buffer[-1] = acc_world
    segs = [[trail_buffer[i],trail_buffer[i+1]] for i in range(TRAIL_LENGTH-1)]
    cols = [(0.15*(1-i/TRAIL_LENGTH),0.5+0.5*(1-i/TRAIL_LENGTH),
             1.0,0.08+0.9*(1-i/TRAIL_LENGTH))
            for i in range(TRAIL_LENGTH-1)]
    trail_segments.set_segments(segs)
    trail_segments.set_color(cols)

    sky,horiz,haze,star_scale,payload_tint,_ = environment_color_profile(alt[frame])
    fig.patch.set_facecolor(sky)
    ax3d.set_facecolor(sky)
    horizon_line.set_color(horiz)

    if haze>0:
        haze_rgb=(0.8,0.85,0.9)
        blended=tuple(sky[i]*(1-haze*0.5)+haze_rgb[i]*(haze*0.5) for i in range(3))
        ax3d.set_facecolor(blended)

    new_star = [(1,1,1,base[3]*star_scale) for base in star_base_colors]
    star_scat.set_facecolors(new_star)
    star_scat.set_edgecolors(new_star)

    tint_rgb=np.clip(cube_facecolor+payload_tint,0,1)
    poly.set_facecolor([tuple(tint_rgb.tolist())])

    lw=6.0*(1.0+2.0*horiz[3])
    horizon_line.set_linewidth(lw)

    alt_marker.set_data([times[frame]],[alt[frame]])
    vel_marker.set_data([times[frame]],[vel[frame]])

    elev=18+np.sin(frame*0.02)*4+(1-np.clip(alt[frame]/32000,0,1))*2.5
    azim=frame*0.45+np.sin(frame*0.03)*8
    ax3d.view_init(elev=elev,azim=azim)

    if impact_frame==-1 and alt[frame]<=5: impact_frame=frame
    if impact_frame!=-1:
        elapsed=(frame-impact_frame)*(dt.mean() if dt.mean()>0 else 0.02)
        if elapsed<2.0:
            flash=max(0,1-(elapsed/2.0))
            flash_col=(1,1,1)
            blended=tuple(flash_col[i]*flash+sky[i]*(1-flash) for i in range(3))
            fig.patch.set_facecolor(blended)
            ax3d.set_facecolor(blended)

    fig.suptitle(
        f"ZR6BN | t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | "
        f"Vel={vel[frame]:.1f} m/s | |a|={np.linalg.norm(acc_body):.1f} m/s² | "
        f"{df['timestamp'].iloc[frame]}",
        fontsize=12, color="white"
    )
    return [poly, trail_segments, alt_marker, vel_marker, horizon_line]

# -----------------------------------------------------------------
# RUN
# -----------------------------------------------------------------
ani = FuncAnimation(fig, update, frames=len(df),
                    interval=dt.mean()*1000/REALTIME_SPEED,
                    blit=False, repeat=False)
plt.tight_layout()
plt.show()

# To record video:
# ani.save("payload_flight_cinematic_troposphere.mp4", fps=30, dpi=150)
