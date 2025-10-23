#!/usr/bin/env python3
"""
BACAR-13 Cinematic Telemetry Simulation
---------------------------------------
- Input: logger/data/MPU6050.txt  (must contain 'timestamp' and 'velocity_m_s')
- Output: simulation/output/BACAR13_full_simulation_vis.mp4
- One frame per telemetry sample (exact timing)
- GPU-accelerated ffmpeg encoding (RTX 3070 compatible)
- Cinematic 3D payload rod + motion cube + telemetry chart

Author: Nathan Busse / 2025
"""

# ------------------------ IMPORTS ------------------------
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless rendering for stability
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial.transform import Rotation as R
from scipy.signal import savgol_filter
from PIL import Image
import warnings, shutil, time

# ------------------------ CONFIG ------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "MPU6050.txt")
CHART_SVG = os.path.join(PROJECT_ROOT, "plotter", "charts", "mpu_chart.svg")
OUT_DIR = os.path.join(PROJECT_ROOT, "simulation", "output")
OUT_FILE = os.path.join(OUT_DIR, "BACAR13_full_simulation_vis.mp4")
FRAME_DIR = os.path.join(OUT_DIR, "frames_temp")

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
DPI = 150
CUBE_SIZE = 0.14
ACC_SCALE = 0.015
TRAIL_LENGTH = 80
SMOOTH_WINDOW = 51
SMOOTH_POLYORDER = 3
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------ LOAD DATA ------------------------
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"MPU6050 file not found: {DATA_FILE}")

df = pd.read_csv(DATA_FILE, comment="#")
if "timestamp" not in df.columns:
    raise ValueError("File must contain 'timestamp' column")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)
for c in ("velocity_m_s", "accel_x_m_s2", "accel_y_m_s2", "accel_z_m_s2",
          "gyro_x_dps", "gyro_y_dps", "gyro_z_dps"):
    if c not in df.columns:
        df[c] = 0.0

times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
dt[dt <= 0] = np.median(dt[dt > 0]) if np.any(dt > 0) else 1.0
vel = df["velocity_m_s"].to_numpy(float)

# integrate velocity → altitude
alt = np.cumsum(vel * dt)
alt = np.clip(alt, 0.0, 32000.0)

# smooth gyro
gyro = df[["gyro_x_dps","gyro_y_dps","gyro_z_dps"]].to_numpy(float)
if len(gyro) >= 7:
    win = min(SMOOTH_WINDOW, len(gyro) // 2 * 2 + 1)
    if win % 2 == 0: win -= 1
    gyro_sm = np.zeros_like(gyro)
    for i in range(3):
        gyro_sm[:, i] = savgol_filter(gyro[:, i], win, SMOOTH_POLYORDER)
else:
    gyro_sm = gyro.copy()

gyro_rad = np.deg2rad(gyro_sm)
orientations = [R.identity()]
for i in range(1, len(gyro_rad)):
    omega = gyro_rad[i] * dt[i]
    orientations.append(orientations[-1] * R.from_rotvec(omega))
rotations = np.array([r.as_matrix() for r in orientations])

acc_vec = df[["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].to_numpy(float)

# ------------------------ HELPERS ------------------------
def altitude_to_color(h):
    a = np.clip(h / 32000.0, 0, 1)
    if a < 0.4:
        t = a / 0.4
        c = (1-t)*np.array([0.01,0.01,0.02]) + t*np.array([0.08,0.12,0.2])
    else:
        t = (a-0.4)/0.6
        c = (1-t)*np.array([0.08,0.12,0.2]) + t*np.array([0.02,0.03,0.06])
    return tuple(np.clip(c,0,1))

def cube_faces(size):
    L = size/2.0
    v = np.array([[-L,-L,-L],[ L,-L,-L],[ L, L,-L],[-L, L,-L],
                  [-L,-L, L],[ L,-L, L],[ L, L, L],[-L, L, L]])
    faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    return v, faces

def shade_faces(rotmat, faces_idx, verts, base_color=(0.8,0.72,1.0)):
    rv = (rotmat @ verts.T).T
    cols=[]
    L = np.array([0.3,0.5,1.0])
    L = L/np.linalg.norm(L)
    for f in faces_idx:
        n = np.cross(rv[f[1]]-rv[f[0]], rv[f[2]]-rv[f[0]])
        n = n/np.linalg.norm(n) if np.linalg.norm(n)>0 else np.array([0,0,1])
        lam = np.clip(np.dot(n,L),0.1,1.0)
        cols.append(tuple(np.clip(base_color*(0.5+0.5*lam),0,1)))
    return rv, cols

def rod_points(alt):
    z = alt / (np.max(alt)+1e-6) * 2.4
    x = np.zeros_like(z)
    y = np.full_like(z, -0.2)
    return x, y, z-1.2

traj_x, traj_y, traj_z = rod_points(alt)
verts, faces_idx = cube_faces(CUBE_SIZE)

# ------------------------ FIGURE SETUP ------------------------
plt.style.use("dark_background")
fig = plt.figure(figsize=(FRAME_WIDTH/DPI, FRAME_HEIGHT/DPI), dpi=DPI)
ax3d = fig.add_subplot(121, projection="3d")
ax_chart = fig.add_subplot(122)
ax3d.set_box_aspect((1,1,1))
ax3d.set_xlim([-1,1]); ax3d.set_ylim([-1,1]); ax3d.set_zlim([-1.6,1.2])
ax3d.axis("off")
ax_chart.axis("off")

chart_img = None
if os.path.exists(CHART_SVG):
    try:
        chart_img = Image.open(CHART_SVG).convert("RGBA")
        ax_chart.imshow(chart_img)
    except Exception:
        ax_chart.text(0.5,0.5,"Chart load failed",ha="center",va="center",color="white")
else:
    ax_chart.text(0.5,0.5,"mpu_chart.svg not found",ha="center",va="center",color="white")

poly = Poly3DCollection([], edgecolors="#333", linewidths=0.6)
ax3d.add_collection3d(poly)
rod_line, = ax3d.plot(traj_x, traj_y, traj_z, lw=12, color="#111")
past_line, = ax3d.plot([], [], [], lw=2, color="#1BBED6")
future_scat = ax3d.scatter([], [], [], s=26, alpha=0.45, color="#9AD6FF")

# ------------------------ RENDER LOOP ------------------------
print("\n[Phase 1] Rendering all frames to PNGs...")
os.makedirs(FRAME_DIR, exist_ok=True)
start = time.time()
frame_count = len(df)
for i in range(frame_count):
    Rm = rotations[i]
    rv, cols = shade_faces(Rm, faces_idx, verts)
    cx, cy, cz = traj_x[i], traj_y[i], traj_z[i]
    faces = [[rv[idx]+np.array([cx,cy,cz]) for idx in f] for f in faces_idx]
    poly.set_verts(faces)
    poly.set_facecolor(cols)

    past_idx = np.arange(i+1)
    fut_idx = np.arange(i+1, len(traj_z), max(1,len(traj_z)//24))
    past_line.set_data(traj_x[past_idx], traj_y[past_idx])
    past_line.set_3d_properties(traj_z[past_idx])
    future_scat._offsets3d = (traj_x[fut_idx], traj_y[fut_idx], traj_z[fut_idx])

    bg = altitude_to_color(alt[i])
    fig.patch.set_facecolor(bg)
    ax3d.set_facecolor(bg)
    fig.suptitle(f"BACAR-13 | t={times[i]:.1f}s | Alt={alt[i]:.0f} m",
                 fontsize=14, color="white", y=0.96)

    frame_path = os.path.join(FRAME_DIR, f"frame_{i:05d}.png")
    fig.savefig(frame_path, dpi=DPI, facecolor=fig.get_facecolor())
    if i % 100 == 0:
        print(f"Rendered {i}/{frame_count} frames...")

print(f"[Phase 1] Done in {time.time()-start:.1f}s")

# ------------------------ ENCODE VIDEO ------------------------
print("\n[Phase 2] Encoding video with GPU...")
ffmpeg_cmd = (
    f"ffmpeg -y -framerate 30 -pattern_type glob "
    f"-i '{FRAME_DIR}/frame_*.png' -c:v h264_nvenc -preset slow "
    f"-pix_fmt yuv420p -b:v 15M '{OUT_FILE}'"
)
print("Running:", ffmpeg_cmd)
ret = os.system(ffmpeg_cmd)
if ret == 0:
    print(f"\n✅ Export complete -> {OUT_FILE}")
else:
    print(f"\n⚠️ ffmpeg returned error code {ret}")

shutil.rmtree(FRAME_DIR, ignore_errors=True)
print("[Cleanup] Temporary frames deleted.")
