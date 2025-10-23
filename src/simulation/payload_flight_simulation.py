#!/usr/bin/env python3
"""
payload_flight_simulation_split.py
Split-screen cinematic BACAR-13 simulator:
 Left: cinematic payload rod + shaded lilac cube (large)
 Right: flat MPU6050 chart (svg -> image) or placeholder
 Exports: FullHD MP4, 1 frame per telemetry sample (exact telemetry playback)
"""

import os, sys, math, time, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # headless rendering for stability
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial.transform import Rotation as R
from scipy.signal import savgol_filter
from PIL import Image
from tqdm import tqdm
import warnings
import subprocess

# ---------------- CONFIG ----------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "MPU6050.txt")
CHART_SVG  = os.path.join(PROJECT_ROOT, "plotter", "charts", "mpu_chart.svg")
OUT_DIR    = os.path.join(PROJECT_ROOT, "simulation", "output")
FRAME_DIR  = os.path.join(OUT_DIR, "frames_temp")
OUT_FILE   = os.path.join(OUT_DIR, "BACAR13_simulation_split.mp4")

W, H = 1920, 1080
DPI = 150
FPS = 30                # encoder framerate
MAX_ALT_M = 32000.0     # burst altitude
CUBE_SIZE = 0.18
TRAIL_LEN = 80
SMOOTH_WIN = 51
SMOOTH_POLY = 3

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

# ---------------- LOAD TELEMETRY ----------------
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"Telemetry not found: {DATA_FILE}")

df = pd.read_csv(DATA_FILE, comment="#")
if "timestamp" not in df.columns:
    raise ValueError("MPU6050.txt must contain 'timestamp' column")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)
df = df.sort_values("timestamp").reset_index(drop=True)

# Ensure numeric columns exist
for c in ("velocity_m_s","accel_x_m_s2","accel_y_m_s2","accel_z_m_s2",
          "gyro_x_dps","gyro_y_dps","gyro_z_dps","altitude_m"):
    if c not in df.columns:
        df[c] = np.nan

# Interpolate numeric columns where possible
numcols = df.select_dtypes(include=[np.number]).columns
df[numcols] = df[numcols].interpolate().fillna(np.nan)

# compute dt in seconds, fix non-positive dt
times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
if np.any(dt <= 0):
    pos = dt[dt > 0]
    dt[dt <= 0] = np.mean(pos) if len(pos) else 1.0

# ---------------- ALTITUDE (use altitude / integrate / synthesize) ----------------
if not df["altitude_m"].isna().all():
    alt = df["altitude_m"].to_numpy(dtype=float)
elif not df["velocity_m_s"].isna().all():
    vel = df["velocity_m_s"].to_numpy(dtype=float)
    alt = np.zeros(len(df))
    for i in range(1, len(df)):
        alt[i] = alt[i-1] + vel[i]*dt[i]
    alt = np.clip(alt, 0.0, MAX_ALT_M*1.05)
else:
    # synthesize plausible ascent → burst → descent to match your confirmation (32km)
    accel_present = not df[["accel_x_m_s2","accel_y_m_s2","accel_z_m_s2"]].isna().all().all()
    burst_idx = None
    if accel_present:
        ax = df["accel_x_m_s2"].fillna(0).to_numpy()
        ay = df["accel_y_m_s2"].fillna(0).to_numpy()
        az = df["accel_z_m_s2"].fillna(0).to_numpy()
        mag = np.sqrt(ax*ax + ay*ay + az*az)
        if len(mag)>0:
            cand = int(np.argmax(mag))
            if mag[cand] > np.median(mag)*2:
                burst_idx = cand
    if burst_idx is None:
        burst_idx = len(df)//2
    climb = np.linspace(0.0, MAX_ALT_M, burst_idx, endpoint=False) if burst_idx>0 else np.array([])
    descent = np.linspace(MAX_ALT_M, 0.0, len(df)-burst_idx) if len(df)-burst_idx>0 else np.array([])
    alt = np.concatenate([climb, descent])
    if len(alt) < len(df):
        alt = np.pad(alt, (0, len(df)-len(alt)), 'edge')
    alt = alt[:len(df)]

alt = np.clip(alt, 0.0, MAX_ALT_M*1.05)

# ---------------- GYRO SMOOTH + ORIENTATION SAFE INTEGRATION ----------------
gyro = df[["gyro_x_dps","gyro_y_dps","gyro_z_dps"]].to_numpy(dtype=float)
n = len(gyro)
if n >= 7:
    win = SMOOTH_WIN if SMOOTH_WIN < n else (n // 2) * 2 + 1
    if win % 2 == 0: win -= 1
    try:
        gyro_sm = np.zeros_like(gyro)
        for i in range(3):
            gyro_sm[:,i] = savgol_filter(gyro[:,i], win, SMOOTH_POLY)
    except Exception:
        gyro_sm = gyro.copy()
else:
    gyro_sm = gyro.copy()

gyro_rad = np.deg2rad(gyro_sm)
orientations = [R.identity()]
for i in range(1, len(gyro_rad)):
    omega = gyro_rad[i] * dt[i]
    if not np.isfinite(omega).all():
        omega = np.zeros(3)
    norm = np.linalg.norm(omega)
    # Ignore tiny / absurd rotations
    if norm < 1e-12 or norm > 1e2:
        omega = np.zeros(3)
    try:
        delta = R.from_rotvec(omega)
    except Exception:
        delta = R.identity()
    orientations.append(orientations[-1] * delta)
    if i % 1000 == 0:
        q = orientations[-1].as_quat()
        qn = np.linalg.norm(q)
        if qn > 0:
            orientations[-1] = R.from_quat(q / qn)
rotations = np.array([r.as_matrix() for r in orientations])

# ---------------- VISUAL HELPERS ----------------
def altitude_to_color(h):
    a = np.clip(h / MAX_ALT_M, 0, 1)
    # cinematic mapping (dark -> teal-ish sky)
    if a < 0.25:
        t = a/0.25
        base = np.array([0.02,0.02,0.03])
        sky  = np.array([0.09,0.12,0.18])
    elif a < 0.75:
        t = (a-0.25)/0.5
        base = np.array([0.09,0.12,0.18])
        sky  = np.array([0.04,0.06,0.12])
    else:
        t = (a-0.75)/0.25
        base = np.array([0.04,0.06,0.12])
        sky  = np.array([0.01,0.02,0.06])
    return tuple(((1-t)*base + t*sky).clip(0,1))

def cube_geometry(size):
    L = size/2.0
    verts = np.array([[-L,-L,-L],[ L,-L,-L],[ L, L,-L],[-L, L,-L],
                      [-L,-L, L],[ L,-L, L],[ L, L, L],[-L, L, L]])
    faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    return verts, faces

def shade_faces(rotmat, faces_idx, verts, base=(0.78,0.72,1.0)):
    rv = (rotmat @ verts.T).T
    facecols = []
    light = np.array([0.25,0.45,1.0])
    light = light / np.linalg.norm(light)
    for f in faces_idx:
        p0,p1,p2 = rv[f[0]], rv[f[1]], rv[f[2]]
        n = np.cross(p1-p0, p2-p0)
        norm = np.linalg.norm(n)
        n = n / norm if norm>0 else np.array([0,0,1.0])
        lam = np.clip(np.dot(n, light), 0.12, 1.0)
        facecols.append(tuple(np.clip(base * (0.45 + 0.55*lam), 0, 1)))
    return rv, facecols

# ---------------- Prepare scene assets ----------------
verts, faces_idx = cube_geometry(CUBE_SIZE)
traj_x = np.zeros_like(alt)
traj_y = np.full_like(alt, -0.25)
traj_z = alt / (np.max(alt)+1e-6) * 2.4 - 1.2

# load chart image if present
chart_img = None
if os.path.exists(CHART_SVG):
    try:
        chart_img = Image.open(CHART_SVG).convert("RGBA")
    except Exception:
        chart_img = None

# ---------------- Matplotlib figure (split layout) ----------------
fig = plt.figure(figsize=(W/DPI, H/DPI), dpi=DPI)
# left large cinematic area (approx 65% width)
left_ax = fig.add_axes([0.0, 0.0, 0.66, 1.0], projection='3d')
left_ax.set_box_aspect((1,1,1))
left_ax.axis("off")
left_ax.set_xlim([-1.0, 1.0]); left_ax.set_ylim([-1.0, 1.0]); left_ax.set_zlim([-1.6, 1.2])

# right chart area (flat)
right_ax = fig.add_axes([0.68, 0.03, 0.30, 0.94])
right_ax.axis("off")
if chart_img is not None:
    right_ax.imshow(chart_img)
else:
    right_ax.set_facecolor("#0F0F0F")
    right_ax.text(0.5,0.5,"mpu_chart.svg\nnot found", ha="center", va="center", color="white", fontsize=16)

# static rod (thick cylinder illusion via a thick 3D line)
rod_line, = left_ax.plot(traj_x, traj_y, traj_z, lw=26, solid_capstyle='round', color="#101216", alpha=0.95)
# past trajectory (thin)
past_line, = left_ax.plot([], [], [], lw=1.6, color=(0.8,0.9,1.0,0.6))
# cube poly placeholder
poly = Poly3DCollection([], facecolors=[(0.78,0.72,1.0)], edgecolors="#2a2a2a", linewidths=0.5, alpha=1.0)
left_ax.add_collection3d(poly)
# future dots (small)
future_scat = left_ax.scatter([], [], [], s=18, color=(0.55,0.7,0.95,0.35))

# faint star-like speckling for background optionally
rng = np.random.RandomState(42)
for _ in range(60):
    xs = rng.uniform(-3,3)
    ys = rng.uniform(-3,3)
    zs = rng.uniform(-3,3)
    left_ax.scatter(xs, ys, zs, s=rng.uniform(1,4), color=(1,1,1,rng.uniform(0.02,0.06)), depthshade=False)

# overlay text labels (2D overlay)
overlay_ax = fig.add_axes([0,0,1,1], zorder=20)
overlay_ax.axis("off")
overlay_ax.text(0.04, 0.72, "future\nvertical\npayload\ntrajectory", fontsize=26, color="white", va="center")
overlay_ax.text(0.04, 0.45, "payload", fontsize=28, color="white", va="center")
overlay_ax.text(0.04, 0.22, "passed\nvertical\npayload\ntrajectory", fontsize=26, color="white", va="center")
overlay_ax.annotate("", xy=(0.45, 0.75), xytext=(0.15, 0.75),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color="white"))
overlay_ax.annotate("", xy=(0.60, 0.52), xytext=(0.15, 0.52),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color="white"))
overlay_ax.annotate("", xy=(0.40, 0.28), xytext=(0.15, 0.28),
                    xycoords='figure fraction', textcoords='figure fraction',
                    arrowprops=dict(arrowstyle="-|>", lw=3, color="white"))

# ---------------- Render frames -> PNGs (phase 1) ----------------
nframes = len(df)
print(f"Rendering {nframes} frames to PNGs in {FRAME_DIR} ... (this may take a while for long flights)")

for i in tqdm(range(nframes), desc="Render frames", unit="frame"):
    # rotation & faces
    Rm = rotations[i]
    rv, facecols = shade_faces(Rm, faces_idx, verts)

    # translate cube to trajectory point
    cx, cy, cz = traj_x[i], traj_y[i], traj_z[i]
    faces_translated = [[tuple(rv[idx] + np.array([cx, cy, cz])) for idx in f] for f in faces_idx]
    poly.set_verts(faces_translated)
    poly.set_facecolor(facecols)

    # past/future sets
    past_idx = np.arange(0, i+1)
    future_idx_full = np.arange(i+1, nframes)
    if len(past_idx) > 0:
        past_line.set_data(traj_x[past_idx], traj_y[past_idx])
        past_line.set_3d_properties(traj_z[past_idx])
    else:
        past_line.set_data([], [])
        past_line.set_3d_properties([])

    if len(future_idx_full) > 0:
        step = max(1, len(future_idx_full)//28)
        sel = future_idx_full[::step]
        future_scat._offsets3d = (traj_x[sel], traj_y[sel], traj_z[sel])
    else:
        future_scat._offsets3d = ([], [], [])

    # halo glow under cube when below 12 km
    if alt[i] < 12000:
        glow_strength = np.clip((12000.0 - alt[i]) / 12000.0, 0.0, 1.0)
        halo = left_ax.scatter([cx], [cy], [cz - 0.02], s=900*glow_strength,
                               color=(1.0,0.92,0.7,0.06 + 0.26*glow_strength), zorder=6)
    else:
        halo = None

    # background color
    bg = altitude_to_color(alt[i])
    fig.patch.set_facecolor(bg)
    left_ax.set_facecolor(bg)

    # camera motion - slow orbit for cinematic feel
    elev = 18 + math.sin(i * 0.012) * 3.5
    azim = 18 + i * 0.12
    left_ax.view_init(elev=elev, azim=azim)

    # title HUD
    fig.suptitle(f"BACAR-13 | t={times[i]:.1f}s | Alt={alt[i]:.0f} m",
                 fontsize=12, color="white", y=0.96)

    # save frame
    frame_path = os.path.join(FRAME_DIR, f"frame_{i:06d}.png")
    fig.savefig(frame_path, dpi=DPI, facecolor=fig.get_facecolor())
    # cleanup transient artists
    if halo is not None:
        try:
            halo.remove()
        except Exception:
            pass

# ---------------- Encode with ffmpeg (phase 2) ----------------
print("Encoding MP4 with ffmpeg (trying GPU encoder h264_nvenc then fallback).")

# prefer nvenc if available
nvenc_cmd = (
    f"ffmpeg -y -framerate {FPS} -pattern_type glob -i '{FRAME_DIR}/frame_*.png' "
    f"-c:v h264_nvenc -preset slow -pix_fmt yuv420p -b:v 15M '{OUT_FILE}'"
)
libx264_cmd = (
    f"ffmpeg -y -framerate {FPS} -pattern_type glob -i '{FRAME_DIR}/frame_*.png' "
    f"-c:v libx264 -pix_fmt yuv420p -crf 16 '{OUT_FILE}'"
)

def run_cmd(cmd):
    print("running:", cmd)
    res = subprocess.run(cmd, shell=True)
    return res.returncode

ret = run_cmd(nvenc_cmd)
if ret != 0:
    warnings.warn("nvenc encoding failed, falling back to libx264 (software).")
    ret = run_cmd(libx264_cmd)
    if ret != 0:
        raise RuntimeError(f"ffmpeg encoding failed (return code {ret}). See stdout/stderr.")

# cleanup frames
try:
    shutil.rmtree(FRAME_DIR)
except Exception:
    pass

print(f"\nDone. MP4 saved -> {OUT_FILE}")
