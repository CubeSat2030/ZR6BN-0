import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation as R

# ===============================================================
# CONFIGURATION
# ===============================================================
FILE = "MPU6050.txt"
REALTIME_SPEED = 1.0       # 1 = real time, 2 = 2× faster
CUBE_SIZE = 0.1            # meters
ACC_SCALE = 0.015          # acceleration arrow scale
TRAIL_LENGTH = 60          # frames to keep in fading trail
START_TIME = "2025-10-11 08:00:00.000"
END_TIME   = "2025-10-11 11:00:00.000"

# ===============================================================
# LOAD DATA
# ===============================================================
df = pd.read_csv(FILE, comment="#")
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df[(df['timestamp'] >= START_TIME) & (df['timestamp'] <= END_TIME)]
df = df.interpolate().fillna(0)

times = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])

gyro = df[['gyro_x_dps','gyro_y_dps','gyro_z_dps']].to_numpy() * np.pi/180.0  # rad/s
accel = df[['accel_x_m_s2','accel_y_m_s2','accel_z_m_s2']].to_numpy()
vel = df['velocity_m_s'].to_numpy() if 'velocity_m_s' in df else np.zeros(len(df))
alt = np.zeros(len(df))
for i in range(1, len(df)):
    alt[i] = alt[i-1] + vel[i]*dt[i]

# ===============================================================
# ORIENTATION INTEGRATION
# ===============================================================
orientations = [R.identity()]
for i in range(1, len(df)):
    omega = gyro[i]*dt[i]
    orientations.append(orientations[-1]*R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

# ===============================================================
# PAYLOAD CUBE
# ===============================================================
L = CUBE_SIZE / 2
verts = np.array([
    [-L,-L,-L],[+L,-L,-L],[+L,+L,-L],[-L,+L,-L],
    [-L,-L,+L],[+L,-L,+L],[+L,+L,+L],[-L,+L,+L]
])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],
         [2,3,7,6],[1,2,6,5],[0,3,7,4]]

# ===============================================================
# PLOT SETUP
# ===============================================================
plt.style.use("dark_background")
fig = plt.figure(figsize=(14,7))
gs = fig.add_gridspec(2,2,width_ratios=[1.1,1.3])
ax_alt = fig.add_subplot(gs[0,0])
ax_vel = fig.add_subplot(gs[1,0])
ax3d   = fig.add_subplot(gs[:,1], projection="3d")

for a in [ax_alt, ax_vel]:
    a.grid(True, alpha=0.3)

ax_alt.set_title("Altitude profile")
ax_alt.set_ylabel("Altitude (m)")
ax_vel.set_title("Vertical velocity")
ax_vel.set_ylabel("Velocity (m/s)")
ax_vel.set_xlabel("Time (s)")

ax3d.set_xlim([-L*3, L*3]); ax3d.set_ylim([-L*3, L*3]); ax3d.set_zlim([-L*3, L*3])
ax3d.set_xlabel("X (m)"); ax3d.set_ylabel("Y (m)"); ax3d.set_zlabel("Z (m)")

alt_line, = ax_alt.plot(times, alt, color="#42A5F5", lw=1)
vel_line, = ax_vel.plot(times, vel, color="#EF5350", lw=1)
alt_marker, = ax_alt.plot([], [], "o", color="gold")
vel_marker, = ax_vel.plot([], [], "o", color="gold")

poly = Poly3DCollection([], facecolors='gold', edgecolors='black', lw=0.5, alpha=0.9)
ax3d.add_collection3d(poly)
acc_vec = ax3d.quiver(0,0,0,0,0,0,color='red',lw=2,arrow_length_ratio=0.3)
trail_segments = [Line3DCollection([], colors=[(1,0,0,0.1)], lw=2)]
ax3d.add_collection3d(trail_segments[0])

fig.suptitle("ZR6BN Payload Flight — Orientation + Telemetry", fontsize=16)

# ===============================================================
# ANIMATION UPDATE
# ===============================================================
trail_buffer = np.zeros((TRAIL_LENGTH, 3))

def update(frame):
    Rm = rotations[frame]
    rotated = (Rm @ verts.T).T
    poly.set_verts([[rotated[i] for i in f] for f in faces])

    acc_body = accel[frame]
    acc_world = Rm @ (acc_body * ACC_SCALE)

    global acc_vec
    acc_vec.remove()
    acc_vec = ax3d.quiver(0,0,0,acc_world[0],acc_world[1],acc_world[2],
                          color='red',lw=2,arrow_length_ratio=0.3)

    # trail update
    trail_buffer[:-1] = trail_buffer[1:]
    trail_buffer[-1] = acc_world
    segments = [[trail_buffer[i], trail_buffer[i+1]] for i in range(TRAIL_LENGTH-1)]
    alphas = np.linspace(0.05, 0.9, TRAIL_LENGTH-1)
    colors = [(1,0,0,a) for a in alphas]
    trail_segments[0].set_segments(segments)
    trail_segments[0].set_color(colors)

    # telemetry markers
    alt_marker.set_data([times[frame]],[alt[frame]])
    vel_marker.set_data([times[frame]],[vel[frame]])

    ax3d.view_init(elev=20, azim=frame*0.4)
    fig.suptitle(
        f"ZR6BN | t={times[frame]:.1f}s | Alt={alt[frame]:.0f} m | "
        f"Vel={vel[frame]:.1f} m/s | |a|={np.linalg.norm(acc_body):.1f} m/s² | "
        f"{df['timestamp'].iloc[frame]}",
        fontsize=13
    )
    return [poly, acc_vec, trail_segments[0], alt_marker, vel_marker]

ani = FuncAnimation(fig, update, frames=len(df),
                    interval=dt.mean()*1000/REALTIME_SPEED, blit=False, repeat=False)
plt.tight_layout()
plt.show()

# --- Optional save ---
# ani.save("payload_flight_trail_fade.mp4", fps=30, dpi=150)
