#!/usr/bin/env python3
"""
BACAR-13 Cinematic Payload Flight Simulation
--------------------------------------------
• Split-screen cinematic simulator (Left: 3D payload, Right: MPU6050 chart)
• One frame per telemetry sample (true playback)
• Auto-derives FPS from timestamps (≈10 Hz)
• Exports a single 1920×1080 MP4 using ffmpeg (h264_nvenc → libx264 fallback)
"""

import os, sys, math, shutil, warnings, subprocess
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
from scipy.signal import savgol_filter
from PIL import Image
from tqdm import tqdm

# ---------------- CONFIG ----------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(PROJECT_ROOT, "logger", "data", "MPU6050.txt")
CHART_SVG  = os.path.join(PROJECT_ROOT, "plotter", "charts", "mpu_chart.svg")
OUT_DIR    = os.path.join(PROJECT_ROOT, "simulation", "output")
FRAME_DIR  = os.path.join(OUT_DIR, "frames_temp")
OUT_FILE   = os.path.join(OUT_DIR, "BACAR13_simulation_split.mp4")

W, H = 1920, 1080
DPI = 150
MAX_ALT_M = 32000.0
CUBE_SIZE = 0.18
SMOOTH_WIN, SMOOTH_POLY = 51, 3
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

# ---------------- LOAD TELEMETRY ----------------
df = pd.read_csv(DATA_FILE, comment="#")
if "timestamp" not in df.columns:
    raise ValueError("Telemetry must have 'timestamp' column")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).reset_index(drop=True)
df = df.sort_values("timestamp").reset_index(drop=True)

# ensure numeric cols
for c in ("velocity_m_s","accel_x_m_s2","accel_y_m_s2","accel_z_m_s2",
          "gyro_x_dps","gyro_y_dps","gyro_z_dps","altitude_m"):
    if c not in df.columns:
        df[c] = np.nan

numcols = df.select_dtypes(include=[np.number]).columns
df[numcols] = df[numcols].interpolate().fillna(method="bfill").fillna(method="ffill")

times = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds().values
dt = np.diff(times, prepend=times[0])
dt[dt <= 0] = np.median(dt[dt > 0]) if np.any(dt > 0) else 0.1

# derive altitude
if not df["altitude_m"].isna().all():
    alt = df["altitude_m"].to_numpy(float)
elif not df["velocity_m_s"].isna().all():
    vel = df["velocity_m_s"].to_numpy(float)
    alt = np.cumsum(vel * dt)
else:
    burst = len(df)//2
    alt = np.concatenate([
        np.linspace(0, MAX_ALT_M, burst, endpoint=False),
        np.linspace(MAX_ALT_M, 0, len(df)-burst)
    ])
alt = np.clip(alt, 0, MAX_ALT_M)

# ---------------- ORIENTATION ----------------
gyro = df[["gyro_x_dps","gyro_y_dps","gyro_z_dps"]].to_numpy(float)
n = len(gyro)
if n >= 7:
    win = min(SMOOTH_WIN, n - (1-n%2))
    gyro_sm = np.column_stack([savgol_filter(gyro[:,i], win, SMOOTH_POLY) for i in range(3)])
else:
    gyro_sm = gyro.copy()

gyro_rad = np.deg2rad(gyro_sm)
orientations = [R.identity()]
for i in range(1, len(gyro_rad)):
    omega = gyro_rad[i]*dt[i]
    norm = np.linalg.norm(omega)
    if not np.isfinite(norm) or norm < 1e-9 or norm > 1e2:
        omega[:] = 0
    try:
        delta = R.from_rotvec(omega)
    except ValueError:
        delta = R.identity()
    orientations.append(orientations[-1]*delta)
    if i % 1000 == 0:
        q = orientations[-1].as_quat()
        orientations[-1] = R.from_quat(q/np.linalg.norm(q))
rotations = np.array([r.as_matrix() for r in orientations])

# ---------------- HELPERS ----------------
def altitude_to_color(h):
    a = np.clip(h/MAX_ALT_M,0,1)
    if a < 0.25:
        t=a/0.25; base=np.array([0.02,0.02,0.03]); sky=np.array([0.09,0.12,0.18])
    elif a < 0.75:
        t=(a-0.25)/0.5; base=np.array([0.09,0.12,0.18]); sky=np.array([0.04,0.06,0.12])
    else:
        t=(a-0.75)/0.25; base=np.array([0.04,0.06,0.12]); sky=np.array([0.01,0.02,0.06])
    return tuple(((1-t)*base + t*sky).clip(0,1))

def cube_geometry(size):
    L=size/2; v=np.array([[-L,-L,-L],[L,-L,-L],[L,L,-L],[-L,L,-L],
                          [-L,-L,L],[L,-L,L],[L,L,L],[-L,L,L]])
    f=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    return v,f

def shade_faces(rot,faces,verts,base=(0.78,0.72,1.0)):
    rv=(rot@verts.T).T; light=np.array([0.25,0.45,1.0]); light/=np.linalg.norm(light)
    cols=[]
    for f in faces:
        n=np.cross(rv[f[1]]-rv[f[0]], rv[f[2]]-rv[f[0]])
        n/=np.linalg.norm(n) if np.linalg.norm(n)>0 else 1
        lam=np.clip(np.dot(n,light),0.12,1.0)
        cols.append(tuple(np.clip(base*(0.45+0.55*lam),0,1)))
    return rv,cols

# ---------------- SCENE ----------------
verts, faces = cube_geometry(CUBE_SIZE)
traj_x = np.zeros_like(alt)
traj_y = np.full_like(alt,-0.25)
traj_z = alt/np.nanmax(alt)*2.4 - 1.2

chart_img=None
if os.path.exists(CHART_SVG):
    try: chart_img=Image.open(CHART_SVG).convert("RGBA")
    except: pass

fig=plt.figure(figsize=(W/DPI,H/DPI),dpi=DPI)
left=fig.add_axes([0,0,0.66,1],projection="3d")
left.set_box_aspect((1,1,1)); left.axis("off")
left.set_xlim([-1,1]); left.set_ylim([-1,1]); left.set_zlim([-1.6,1.2])
right=fig.add_axes([0.68,0.03,0.30,0.94]); right.axis("off")
if chart_img: right.imshow(chart_img)
else: right.set_facecolor("#0F0F0F")

rod,=left.plot(traj_x,traj_y,traj_z,lw=26,color="#101216",alpha=0.95)
past,=left.plot([],[],[],lw=1.6,color=(0.8,0.9,1,0.6))
poly=Poly3DCollection([],facecolors=[(0.78,0.72,1)],edgecolors="#2a2a2a",lw=0.5)
left.add_collection3d(poly)
future=left.scatter([],[],[],s=18,color=(0.55,0.7,0.95,0.35))

# ---------------- FPS FROM DATA ----------------
total_seconds=(df["timestamp"].iloc[-1]-df["timestamp"].iloc[0]).total_seconds()
FPS=len(df)/total_seconds if total_seconds>0 else 10.0
print(f"⏱ Duration {total_seconds/3600:.2f} h  →  FPS={FPS:.3f}")

# ---------------- FRAME RENDER ----------------
print(f"Rendering {len(df)} frames…")
for i in tqdm(range(len(df)),unit="frame"):
    Rm=rotations[i]
    rv,cols=shade_faces(Rm,faces,verts)
    cx,cy,cz=traj_x[i],traj_y[i],traj_z[i]
    poly.set_verts([[rv[idx]+[cx,cy,cz] for idx in f] for f in faces])
    poly.set_facecolor(cols)
    past.set_data(traj_x[:i+1],traj_y[:i+1]); past.set_3d_properties(traj_z[:i+1])
    step=max(1,(len(df)-i)//28)
    sel=np.arange(i+1,len(df),step)
    future._offsets3d=(traj_x[sel],traj_y[sel],traj_z[sel])
    bg=altitude_to_color(alt[i])
    fig.patch.set_facecolor(bg); left.set_facecolor(bg)
    elev=18+math.sin(i*0.012)*3.5; azim=18+i*0.12
    left.view_init(elev,azim)
    fig.suptitle(f"BACAR-13 | t={times[i]:.1f}s | Alt={alt[i]:.0f} m",fontsize=12,color="white",y=0.96)
    frame=os.path.join(FRAME_DIR,f"frame_{i:06d}.png")
    fig.savefig(frame,dpi=DPI,facecolor=fig.get_facecolor())

# ---------------- ENCODE ----------------
print("Encoding MP4 via ffmpeg…")
cmd_nv=f"ffmpeg -y -framerate {FPS} -pattern_type glob -i '{FRAME_DIR}/frame_*.png' -c:v h264_nvenc -preset slow -pix_fmt yuv420p -b:v 15M '{OUT_FILE}'"
cmd_x264=f"ffmpeg -y -framerate {FPS} -pattern_type glob -i '{FRAME_DIR}/frame_*.png' -c:v libx264 -pix_fmt yuv420p -crf 16 '{OUT_FILE}'"
if subprocess.run(cmd_nv,shell=True).returncode!=0:
    warnings.warn("NVENC failed, using libx264.")
    if subprocess.run(cmd_x264,shell=True).returncode!=0:
        raise RuntimeError("ffmpeg encode failed.")

shutil.rmtree(FRAME_DIR,ignore_errors=True)
print(f"✅ Done → {OUT_FILE}")
