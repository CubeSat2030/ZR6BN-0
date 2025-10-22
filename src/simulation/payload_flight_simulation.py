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
    a.set_facecolor("#000010")  # deep black-blue

ax_alt.set_title("Altitude profile")
ax_alt.set_ylabel("Altitude (m)")
ax_vel.set_title("Vertical velocity")
ax_vel.set_ylabel("Velocity (m/s)")
ax_vel.set_xlabel("Time (s)")

ax3d.set_xlim([-L*4, L*4])
ax3d.set_ylim([-L*4, L*4])
ax3d.set_zlim([-L*4, L*4])
ax3d.set_xlabel("X (m)")
ax3d.set_ylabel("Y (m)")
ax3d.set_zlabel("Z (m)")
ax3d.set_facecolor("#000000")

# Starfield background (dim random dots)
np.random.seed(42)
for _ in range(120):
    ax3d.scatter(
        np.random.uniform(-3, 3),
        np.random.uniform(-3, 3),
        np.random.uniform(-3, 3),
        color=(1,1,1,np.random.uniform(0.02, 0.08)),
        s=np.random.uniform(2,5),
        depthshade=False
    )

alt_line, = ax_alt.plot(times, alt, color="#42A5F5", lw=1)
vel_line, = ax_vel.plot(times, vel, color="#EF5350", lw=1)
alt_marker, = ax_alt.plot([], [], "o", color="gold")
vel_marker, = ax_vel.plot([], [], "o", color="gold")

# Gold cube payload
poly = Poly3DCollection([], facecolors="#FFD54F", edgecolors="#333333", lw=0.4, alpha=0.95)
ax3d.add_collection3d(poly)

# Acceleration vector
acc_vec = ax3d.quiver(0,0,0,0,0,0,color="cyan",lw=2,arrow_length_ratio=0.3)

# Trail setup
dummy_segments = np.array([[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]])
trail_segments = [Line3DCollection(dummy_segments, colors=[(0,1,1,0.2)], lw=2)]
ax3d.add_collection3d(trail_segments[0])
trail_segments[0].set_segments([])

fig.suptitle("ZR6BN Payload Flight — Stratospheric Descent (Cinematic View)", fontsize=15, color="white")

# -----------------------------------------------------------------
# SKY COLOR FUNCTION
# -----------------------------------------------------------------
def altitude_to_color(h):
    """Dark near-space color with faint blue horizon glow near ground."""
    t = np.clip(h / 32000.0, 0, 1)
    r = 0.0 + 0.2*(1 - t)
    g = 0.05 + 0.4*(1 - t)
    b = 0.1 + 0.9*(1 - t/2)
    return (r, g, b)

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

    # Blue trail glow
    trail_buffer[:-1] = trail_buffer[1:]
    trail_buffer[-1] = acc_world
    segments = [[trail_buffer[i], trail_buffer[i+1]] for i in range(TRAIL_LENGTH-1)]
    colors = [
        (0.2*(i/TRAIL_LENGTH), 0.5 + 0.5*(i/TRAIL_LENGTH), 1.0, 0.1 + 0.8*(i/TRAIL_LENGTH))
        for i in range(TRAIL_LENGTH-1)
    ]
    trail_segments[0].set_segments(segments)
    trail_segments[0].set_color(colors)

    # Environment background
    bg = altitude_to_color(alt[frame])
    fig.patch.set_facecolor(bg)
    ax3d.set_facecolor(bg)

    # Horizon glow near surface
    if alt[frame] < 5000:
        horizon_blend = (5000 - alt[frame]) / 5000
        glow_color = (bg[0]+0.2*horizon_blend, bg[1]+0.3*horizon_blend, bg[2]+0.5*horizon_blend)
        ax3d.set_facecolor(glow_color)
        fig.patch.set_facecolor(glow_color)

    alt_marker.set_data([times[frame]], [alt[frame]])
    vel_marker.set_data([times[frame]], [vel[frame]])

    # Cinematic camera motion
    ax3d.view_init(
        elev=20 + np.sin(frame * 0.02) * 4,
        azim=frame * 0.5 + np.sin(frame * 0.03) * 10
    )

    # Impact flash
    if impact_frame == -1 and alt[frame] <= 5:
        impact_frame = frame
    if impact_frame != -1:
        elapsed = (frame - impact_frame) * dt.mean()
        if elapsed < 2.0:
            flash_strength = max(0, 1 - (elapsed / 2.0))
            flash_color = (1.0, 1.0, 1.0)
            blended = tuple(
                flash_color[i] * flash_strength + bg[i] * (1 - flash_strength)
                for i in range(3)
            )
            fig.patch.set_facecolor(blended)
            ax3d.set_facecolor(blended)

    fig.suptitle(
        f"ZR6BN | t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | "
        f"Vel={vel[frame]:.1f} m/s | |a|={np.linalg.norm(acc_body):.1f} m/s² | "
        f"{df['timestamp'].iloc[frame]}",
        fontsize=12,
        color="white"
    )
    return [poly, acc_vec, trail_segments[0], alt_marker, vel_marker]

# -----------------------------------------------------------------
# RUN
# -----------------------------------------------------------------
ani = FuncAnimation(
    fig, update, frames=len(df),
    interval=dt.mean()*1000/REALTIME_SPEED, blit=False, repeat=False
)
plt.tight_layout()
plt.show()
