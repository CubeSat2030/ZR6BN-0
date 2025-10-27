"""
payload_flight_simulation.py

Cinematic, physics-accurate payload flight animation with realistic
troposphere transition (Matplotlib 3.10.3 compatible).

- Reads sensor data from src/logger/data/MPU6050.txt
- Renders a gold payload cube using recorded orientation (gyro-integrated)
- Shows blue ionized trail (fading) and acceleration vector
- Adds an altitude-driven environment: space -> stratosphere -> troposphere -> near-surface
- Adds horizon arc, horizon thickening, haze, star fade, and subtle payload tinting
- Impact flash + lingering flare remain in place
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

# Altitude breakpoints (meters)
STRATOPAUSE = 12000.0   # above: stratosphere
MID_TROPO = 5000.0      # transition band
NEAR_SURFACE = 1000.0   # strong haze & ground reflection

# -----------------------------------------------------------------
# LOAD & PREPARE DATA
# -----------------------------------------------------------------
df = pd.read_csv(DATA_FILE, comment="#")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df[(df["timestamp"] >= START_TIME) & (df["timestamp"] <= END_TIME)]
df = df.interpolate().fillna(0)
df = df.sort_values(by="timestamp").reset_index(drop=True)

times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])

gyro = df[["gyro_x_dps", "gyro_y_dps", "gyro_z_dps"]].to_numpy() * np.pi / 180.0
accel = df[["accel_x_m_s2", "accel_y_m_s2", "accel_z_m_s2"]].to_numpy()
vel = df["velocity_m_s"].to_numpy() if "velocity_m_s" in df else np.zeros(len(df))

# Integrate altitude (simple numerical integration of vertical velocity)
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i] * dt[i]
alt = np.clip(alt, 0, 32000)

# -----------------------------------------------------------------
# ORIENTATION INTEGRATION (forward-time)
# -----------------------------------------------------------------
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro[i] * dt[i]
    orientations.append(orientations[-1] * R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

# -----------------------------------------------------------------
# PAYLOAD GEOMETRY
# -----------------------------------------------------------------
L = CUBE_SIZE / 2
verts = np.array([
    [-L, -L, -L], [+L, -L, -L], [+L, +L, -L], [-L, +L, -L],
    [-L, -L, +L], [+L, -L, +L], [+L, +L, +L], [-L, +L, +L]
])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]

# -----------------------------------------------------------------
# FIGURE SETUP
# -----------------------------------------------------------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(14,7))
gs = fig.add_gridspec(2,2, width_ratios=[1.05,1.4])
ax_alt = fig.add_subplot(gs[0,0])
ax_vel = fig.add_subplot(gs[1,0])
ax3d  = fig.add_subplot(gs[:,1], projection="3d")

# Basic subplot styling
for a in (ax_alt, ax_vel):
    a.grid(True, alpha=0.25)
    a.set_facecolor("#000010")

ax_alt.set_title("Altitude profile")
ax_alt.set_ylabel("Altitude (m)")
ax_vel.set_title("Vertical velocity")
ax_vel.set_ylabel("Velocity (m/s)")
ax_vel.set_xlabel("Time (s)")

ax3d.set_xlim([-L*4, L*4]); ax3d.set_ylim([-L*4, L*4]); ax3d.set_zlim([-L*4, L*4])
ax3d.set_xlabel("X (m)"); ax3d.set_ylabel("Y (m)"); ax3d.set_zlabel("Z (m)")
ax3d.set_facecolor("#000000")

# Starfield (as scatter collection; we'll keep references for alpha modulation)
np.random.seed(42)
star_pos = np.random.uniform(-3, 3, size=(120, 3))
star_sizes = np.random.uniform(2, 5, size=120)
star_alphas = np.random.uniform(0.02, 0.08, size=120)
star_scat = ax3d.scatter(star_pos[:,0], star_pos[:,1], star_pos[:,2],
                         color=[(1,1,1,a) for a in star_alphas],
                         s=star_sizes, depthshade=False)

# Telemetry traces
alt_line, = ax_alt.plot(times, alt, color="#42A5F5", lw=1)
vel_line, = ax_vel.plot(times, vel, color="#EF5350", lw=1)
alt_marker, = ax_alt.plot([], [], "o", color="gold")
vel_marker, = ax_vel.plot([], [], "o", color="gold")

# Payload cube and initial colors (we'll tint facecolors dynamically)
cube_facecolor = np.array([1.0, 0.84, 0.33])  # gold base
poly = Poly3DCollection([], facecolors=[cube_facecolor], edgecolors="#333333", lw=0.4, alpha=0.95)
ax3d.add_collection3d(poly)

# Acceleration vector (quiver as a Line3D-like segment)
acc_vec = ax3d.quiver(0,0,0,0,0,0, color="cyan", lw=2, arrow_length_ratio=0.3)

# Trail (Line3DCollection)
dummy_segments = np.array([[[0.0,0.0,0.0],[0.0,0.0,0.0]]])
trail_segments = Line3DCollection(dummy_segments, colors=[(0.4,0.8,1.0,0.2)], lw=2)
ax3d.add_collection3d(trail_segments)
trail_segments.set_segments([])

fig.suptitle("ZR6BN Payload Flight — Cinematic (Troposphere Transition)", fontsize=14, color="white")

# -----------------------------------------------------------------
# ENVIRONMENT MODEL: altitude -> sky/horizon/haze/payload tint
# -----------------------------------------------------------------
def environment_color_profile(h):
    """
    Returns:
      sky_color (r,g,b), horizon_rgba (r,g,b,a), haze_alpha (0..1),
      star_alpha_scale (0..1), payload_tint (r,g,b, tint_strength)
    based on altitude h in meters.
    Realistic transitions:
      - > STRATOPAUSE: near-black, visible stars, thin horizon
      - between STRATOPAUSE and MID_TROPO: gradual blueening
      - below MID_TROPO and above NEAR_SURFACE: haze increases
      - below NEAR_SURFACE: strong near-surface scattering & ground tint
    """
    t_s = np.clip((h - STRATOPAUSE) / (32000 - STRATOPAUSE), 0, 1)  # 1 high (space)
    # sky: interpolate between near-black (space) and pale sky
    sky_space = np.array([0.01, 0.02, 0.06])     # deep upper sky (navy-black)
    sky_tropo = np.array([0.72, 0.9, 0.98])      # bright pale-sky near surface
    # inversion: when h large -> use space; when h small -> tropo
    sky_mix = (t_s * sky_space) + ((1 - t_s) * sky_tropo)

    # horizon base color and alpha depend on altitude
    horizon_base = np.array([0.5, 0.78, 1.0])  # cyan-white
    # horizon alpha increases rapidly when below ~5000 m
    horizon_alpha = np.clip((8000 - h) / 8000, 0.0, 0.95)  # starts rising under 8km
    horizon_rgba = (horizon_base[0], horizon_base[1], horizon_base[2], 0.05 + 0.95*horizon_alpha)

    # haze (aerosol scattering) strength: small above mid_tropo, rises below
    if h > MID_TROPO:
        haze = 0.0
    elif h > NEAR_SURFACE:
        haze = np.clip((MID_TROPO - h) / (MID_TROPO - NEAR_SURFACE), 0.0, 0.7)
    else:
        haze = 0.9

    # star visibility scale: 1 at high altitude, drops to 0 under troposphere
    star_scale = np.clip((h - MID_TROPO) / (32000 - MID_TROPO), 0.0, 1.0)

    # payload tinting: slight bluish tint as scattering increases
    tint_strength = np.clip((MID_TROPO - h) / (MID_TROPO), 0.0, 0.6)
    payload_tint = np.array([0.35, 0.55, 0.95]) * tint_strength  # bluish tint vector

    return tuple(sky_mix), horizon_rgba, haze, star_scale, tuple(payload_tint), tint_strength

# -----------------------------------------------------------------
# ANIMATION STATE
# -----------------------------------------------------------------
trail_buffer = np.zeros((TRAIL_LENGTH, 3))
impact_frame = -1

# Precompute star base colors (RGBA) to allow alpha scaling per frame
star_base_colors = [(1.0,1.0,1.0, a) for a in star_alphas]

# -----------------------------------------------------------------
# UPDATE FUNCTION
# -----------------------------------------------------------------
def update(frame):
    global impact_frame

    # 1) Payload orientation + geometry
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])

    # 2) Acceleration vector (body -> world)
    acc_body = accel[frame]
    acc_world = Rm @ (acc_body * ACC_SCALE)

    # Update quiver via set_segments on the internal Line3D representation (Matplotlib quiver in 3D is limited)
    # For compatibility we'll remove/add the quiver by re-creating (safe for Matplotlib 3.10.3)
    # remove previous by setting to zero-length and then draw new
    # Note: using ax3d.quiver each frame is acceptable for moderate frame counts; keep as-is.
    # Remove old by hiding (no deletion required in this context); instead update by re-creating
    for coll in list(ax3d.collections):
        # avoid removing the cube and the trail collections by checking types/ids
        pass
    # Simpler approach: set acc_vec by reassigning new quiver and removing old (fast enough)
    try:
        acc_vec.remove()
    except Exception:
        pass
    # create new quiver for this frame
    ax3d.quiver(0,0,0, acc_world[0], acc_world[1], acc_world[2],
               color="cyan", linewidth=1.5, arrow_length_ratio=0.25)
    # Note: we don't keep handle reference to reduce complexity across frames

    # 3) Trail update (fading blue trail)
    trail_buffer[:-1] = trail_buffer[1:]
    trail_buffer[-1] = acc_world
    segments = [[trail_buffer[i], trail_buffer[i+1]] for i in range(TRAIL_LENGTH - 1)]
    # gradient: newest bright cyan -> older deep blue (alpha increases for newest)
    colors = [
        (0.15 * (1 - i / TRAIL_LENGTH), 0.5 + 0.5*(1 - i / TRAIL_LENGTH), 1.0, 0.08 + 0.9*(1 - i / TRAIL_LENGTH))
        for i in range(TRAIL_LENGTH - 1)
    ]
    trail_segments.set_segments(segments)
    trail_segments.set_color(colors)

    # 4) Environment: sky color, horizon, haze, stars, payload tint
    sky_color, horizon_rgba, haze_alpha, star_scale, payload_tint, tint_strength = environment_color_profile(alt[frame])
    # set figure and axis backgrounds
    fig.patch.set_facecolor(sky_color)
    ax3d.set_facecolor(sky_color)
    # horizon arc (precomputed below) updated by setting color/alpha
    horizon_strength = horizon_rgba[3]
    # mix horizon color with sky (slightly brighter)
    horizon_color = (horizon_rgba[0], horizon_rgba[1], horizon_rgba[2], horizon_rgba[3])
    horizon_line.set_color(horizon_color)

    # haze effect: adjust axis face alpha by blending with a grey haze overlay
    if haze_alpha > 0.0:
        haze_rgb = (0.8, 0.85, 0.9)
        blended = tuple(sky_color[i] * (1 - haze_alpha*0.5) + haze_rgb[i] * (haze_alpha*0.5) for i in range(3))
        ax3d.set_facecolor(blended)
    else:
        ax3d.set_facecolor(sky_color)

    # stars alpha modulation
    new_star_rgba = []
    for i, base in enumerate(star_base_colors):
        a = base[3] * star_scale
        new_star_rgba.append((1.0,1.0,1.0,a))
    # Update star scatter facecolors
    star_scat.set_facecolors(new_star_rgba)
    star_scat.set_edgecolors(new_star_rgba)

    # 5) Slight payload tinting due to atmospheric scattering (modify facecolors)
    tint_rgb = np.array(cube_facecolor) + np.array(payload_tint)
    tint_rgb = np.clip(tint_rgb, 0, 1)
    # Use uniform facecolor tint for cube
    poly.set_facecolor([tuple(tint_rgb.tolist())])

    # 6) Horizon glow intensity increases as altitude decreases
    # horizon_line color handled above; widen linewidth when near
    lw = 6.0 * (1.0 + 2.0 * horizon_strength)
    horizon_line.set_linewidth(lw)

    # 7) Telemetry markers update
    alt_marker.set_data([times[frame]], [alt[frame]])
    vel_marker.set_data([times[frame]], [vel[frame]])

    # 8) Cinematic camera: gentle orbit + slight zoom tied to altitude
    # zoom: as altitude decreases, move camera slightly closer
    zoom_factor = 1.0 + 0.8 * (1 - np.clip(alt[frame] / 32000.0, 0, 1))
    elev = 18 + np.sin(frame * 0.02) * 4.0 + (1 - np.clip(alt[frame] / 32000.0, 0, 1)) * 2.5
    azim = frame * 0.45 + np.sin(frame * 0.03) * 8.0
    ax3d.view_init(elev=elev, azim=azim)

    # 9) Impact flash + lingering flare
    if impact_frame == -1 and alt[frame] <= 5:
        # mark once
        globals()['impact_frame'] = frame
        impact_frame_local = frame
    if 'impact_frame' in globals():
        elapsed = (frame - globals()['impact_frame']) * (dt.mean() if dt.mean() > 0 else 0.02)
        if elapsed < 2.0:
            flash_strength = max(0, 1 - (elapsed / 2.0))
            flash_color = (1.0, 1.0, 1.0)
            blended = tuple(flash_color[i] * flash_strength + sky_color[i] * (1 - flash_strength) for i in range(3))
            fig.patch.set_facecolor(blended)
            ax3d.set_facecolor(blended)

    # 10) Title update
    fig.suptitle(
        f"ZR6BN | t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | "
        f"Vel={vel[frame]:.1f} m/s | |a|={np.linalg.norm(acc_body):.1f} m/s² | "
        f"{df['timestamp'].iloc[frame]}",
        fontsize=12, color="white"
    )

    # Return visual artists (Matplotlib ignores extras from 3D collections sometimes)
    return [poly, trail_segments, alt_marker, vel_marker, horizon_line]

# -----------------------------------------------------------------
# HORIZON ARC (flat curved arc beneath payload)
# -----------------------------------------------------------------
horizon_radius = 2.5
theta = np.linspace(-np.pi/1.5, np.pi/1.5, 300)
x_arc = horizon_radius * np.cos(theta)
y_arc = horizon_radius * np.sin(theta)
z_arc = np.zeros_like(x_arc) - 0.2  # slightly below center
horizon_line, = ax3d.plot(x_arc, y_arc, z_arc, color=(0.3,0.6,1.0,0.0), lw=6, zorder=0)

# -----------------------------------------------------------------
# RUN ANIMATION
# -----------------------------------------------------------------
ani = FuncAnimation(
    fig, update, frames=len(df),
    interval=dt.mean()*1000/REALTIME_SPEED, blit=False, repeat=False
)
plt.tight_layout()
plt.show()

# To save a movie (uncomment):
# ani.save("payload_flight_cinematic_troposphere.mp4", fps=30, dpi=150)
