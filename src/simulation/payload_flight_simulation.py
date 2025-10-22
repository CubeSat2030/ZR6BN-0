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

# -----------------------------------------------------------------
# LOAD DATA
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

# Integrate altitude
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i]*dt[i]
alt = np.clip(alt, 0, 32000)

# -----------------------------------------------------------------
# ORIENTATION INTEGRATION
# -----------------------------------------------------------------
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro[i]*dt[i]
    orientations.append(orientations[-1]*R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

# -----------------------------------------------------------------
# PAYLOAD GEOMETRY
# -----------------------------------------------------------------
L = CUBE_SIZE / 2
verts = np.array([
    [-L,-L,-L],[+L,-L,-L],[+L,+L,-L],[-L,+L,-L],
    [-L,-L,+L],[+L,-L,+L],[+L,+L,+L],[-L,+L,+L]
])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],
         [2,3,7,6],[1,2,6,5],[0,3,7,4]]

# -----------------------------------------------------------------
# FIGURE SETUP — CINEMATIC ENVIRONMENT
# -----------------------------------------------------------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(14,7))
gs = fig.add_gridspec(2,2,width_ratios=[1.1,1.3])
ax_alt = fig.add_subplot(gs[0,0])
ax_vel = fig.add_subplot(gs[1,0])
ax3d   = fig.add_subplot(gs[:,1], projection="3d")

for a in [ax_alt, ax_vel]:
    a.grid(True, alpha=0.25)
    a.set_facecolor("#000010")

ax_alt.set_title("Altitude profile")
ax_alt.set_ylabel("Altitude (m)")
ax_vel.set_title("Vertical velocity")
ax_vel.set_ylabel("Velocity (m/s)")
ax_vel.set_xlabel("Time (s)")

ax3d.set_xlim([-L*4, L*4])
ax3d.set_ylim([-L*4, L*4])
ax3d.set_zlim([-L*4, L*4])
ax3d.set_facecolor("#000000")

# Starfield
np.random.seed(42)
for _ in range(120):
    ax3d.scatter(
        np.random.uniform(-3,3),
        np.random.uniform(-3,3),
        np.random.uniform(-3,3),
        color=(1,1,1,np.random.uniform(0.02,0.08)),
        s=np.random.uniform(2,5),
        depthshade=False
    )

alt_line, = ax_alt.plot(times, alt, color="#42A5F5", lw=1)
vel_line, = ax_vel.plot(times, vel, color="#EF5350", lw=1)
alt_marker, = ax_alt.plot([], [], "o", color="gold")
vel_marker, = ax_vel.plot([], [], "o", color="gold")

# Payload cube
poly = Poly3DCollection([], facecolors="#FFD54F", edgecolors="#333333", lw=0.4, alpha=0.95)
ax3d.add_collection3d(poly)

acc_vec = ax3d.quiver(0,0,0,0,0,0,color="cyan",lw=2,arrow_length_ratio=0.3)

# Trail
dummy_segments = np.array([[[0,0,0],[0,0,0]]])
trail_segments = [Line3DCollection(dummy_segments, colors=[(0,1,1,0.2)], lw=2)]
ax3d.add_collection3d(trail_segments[0])
trail_segments[0].set_segments([])

fig.suptitle("ZR6BN Payload Flight — Stratospheric → Tropospheric Descent",
             fontsize=15, color="white")

# -----------------------------------------------------------------
# SKY COLOR FUNCTION
# -----------------------------------------------------------------
def altitude_to_color(h):
    """Space black to light blue near ground."""
    if h > 12000:  # Stratosphere
        t = np.clip(h / 32000.0, 0, 1)
        r = 0.0 + 0.15*(1 - t)
        g = 0.05 + 0.5*(1 - t)
        b = 0.1 + 1.0*(1 - t/2)
    else:  # Troposphere
        t = np.clip(h / 12000.0, 0, 1)
        r = 0.5 * (1 - t) + 0.1 * t
        g = 0.7 * (1 - t) + 0.3 * t
        b = 1.0 * (1 - t) + 0.5 * t
        haze = 0.2 * (1 - t)
        r += haze
        g += haze * 0.8
        b += haze * 0.6
    return (np.clip(r,0,1), np.clip(g,0,1), np.clip(b,0,1))

# -----------------------------------------------------------------
# HORIZON ARC GENERATION
# -----------------------------------------------------------------
horizon_radius = 2.5  # apparent radius of the arc
theta = np.linspace(-np.pi/1.5, np.pi/1.5, 200)
x_arc = horizon_radius * np.cos(theta)
y_arc = horizon_radius * np.sin(theta)
z_arc = np.zeros_like(x_arc)
horizon_line = ax3d.plot(x_arc, y_arc, z_arc, color=(0.3,0.6,1,0.0), lw=6)[0]

# -----------------------------------------------------------------
# ANIMATION UPDATE
# -----------------------------------------------------------------
trail_buffer = np.zeros((TRAIL_LENGTH, 3))
impact_frame = -1

def update(frame):
    global impact_frame
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])

    acc_body = accel[frame]
    acc_world = Rm @ (acc_body * ACC_SCALE)
    acc_vec.set_segments([[[0,0,0], acc_world]])

    trail_buffer[:-1] = trail_buffer[1:]
    trail_buffer[-1] = acc_world
    segments = [[trail_buffer[i], trail_buffer[i+1]] for i in range(TRAIL_LENGTH-1)]
    colors = [
        (0.2*(i/TRAIL_LENGTH), 0.5+0.5*(i/TRAIL_LENGTH), 1.0, 0.1+0.8*(i/TRAIL_LENGTH))
        for i in range(TRAIL_LENGTH-1)
    ]
    trail_segments[0].set_segments(segments)
    trail_segments[0].set_color(colors)

    # Background & horizon brightness
    bg = altitude_to_color(alt[frame])
    fig.patch.set_facecolor(bg)
    ax3d.set_facecolor(bg)

    # Horizon thickening & aerosol
    horizon_strength = np.clip((5000 - alt[frame]) / 5000, 0, 1)
    horizon_color = (
        0.3 + 0.3*horizon_strength, 
        0.6 + 0.2*horizon_strength, 
        1.0, 
        0.15 + 0.5*horizon_strength
    )
    horizon_line.set_color(horizon_color)
    horizon_line.set_linewidth(4 + 2*horizon_strength)

    # Payload lighting response
    if alt[frame] < 10000:
        ambient_factor = (10000 - alt[frame])/10000
        poly.set_facecolor((1.0, 0.84, 0.4 + 0.1*ambient_factor))

    # Ground bloom — safe handling if no facecolor yet
    if alt[frame] < 1000:
        bloom_strength = (1000 - alt[frame])/1000
        fc = poly.get_facecolor()
        if len(fc) == 0:
            base_color = np.array([1.0, 0.84, 0.4])
        else:
            base_color = np.array(fc[0][:3])
        poly.set_facecolor(tuple(np.clip(base_color + bloom_strength*0.1, 0, 1)))

    # Alt/Vel markers
    alt_marker.set_data([times[frame]], [alt[frame]])
    vel_marker.set_data([times[frame]], [vel[frame]])

    # Camera stabilization
    smooth_factor = np.clip((500 - alt[frame])/500, 0, 1)
    ax3d.view_init(
        elev=20 + np.sin(frame*0.02)*(4*(1-smooth_factor)),
        azim=frame*0.5 + np.sin(frame*0.03)*(10*(1-smooth_factor))
    )

    # Volumetric glow around payload
    if alt[frame] < 12000:
        glow_strength = np.clip((12000 - alt[frame])/12000, 0, 1)
        halo_color = (1.0, 0.84, 0.4 + 0.1*glow_strength, 0.2*glow_strength)
        ax3d.scatter(
            [0], [0], [0],
            s=2000*glow_strength,
            color=halo_color,
            edgecolors='none',
            alpha=halo_color[3]
        )

    # Impact flash
    if impact_frame == -1 and alt[frame] <= 5:
        impact_frame = frame
    if impact_frame != -1:
        elapsed = (frame - impact_frame) * dt.mean()
        if elapsed < 2.0:
            flash_strength = max(0, 1 - elapsed/2)
            flash_color = (1,1,1)
            blended = tuple(flash_color[i]*flash_strength + bg[i]*(1-flash_strength)
                            for i in range(3))
            fig.patch.set_facecolor(blended)
            ax3d.set_facecolor(blended)

    fig.suptitle(
        f"ZR6BN | t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | "
        f"Vel={vel[frame]:.1f} m/s | |a|={np.linalg.norm(acc_body):.1f} m/s² | "
        f"{df['timestamp'].iloc[frame]}",
        fontsize=12, color="white"
    )
    return [poly, acc_vec, trail_segments[0], alt_marker, vel_marker, horizon_line]

# -----------------------------------------------------------------
# RUN
# -----------------------------------------------------------------
ani = FuncAnimation(
    fig, update, frames=len(df),
    interval=dt.mean()*1000/REALTIME_SPEED, blit=False, repeat=False
)
plt.tight_layout()
plt.show()

# To export:
# ani.save("payload_flight_simulation_troposphere_cinematic.mp4", fps=30, dpi=150)
