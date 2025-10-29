#!/usr/bin/env python3
"""
render_stream_interpolated_vectors.py
----------------------------------------------------
Interpolated high-FPS cinematic payload replay with
control rod direction vectors drawn in 3D body frame.
"""
import os, io, subprocess
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

# ---------- CONFIG ----------
DATA_CSV = "../data/trajectory.csv"
OUT_MP4 = "../out/video/hab_sim_control_vectors.mp4"
REAL_FPS = 10
TARGET_FPS = 30
CRF = 18
PRESET = "medium"

# Length of rod direction indicators (in meters)
ROD_LENGTH = 0.5
ROD_COLOR = "orange"
ROD_ALPHA = 0.8
# ----------------------------

def start_ffmpeg(out_path, fps):
    cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe", "-vcodec", "png",
        "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", PRESET,
        "-crf", str(CRF), "-pix_fmt", "yuv420p",
        out_path
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

# Quaternion SLERP
def quat_slerp(q0, q1, t):
    dot = np.dot(q0, q1)
    if dot < 0.0:
        q1 = -q1
        dot = -dot
    DOT_THRESHOLD = 0.9995
    if dot > DOT_THRESHOLD:
        result = q0 + t * (q1 - q0)
        return result / np.linalg.norm(result)
    theta_0 = np.arccos(dot)
    sin_theta_0 = np.sin(theta_0)
    theta = theta_0 * t
    s0 = np.sin(theta_0 - theta) / sin_theta_0
    s1 = np.sin(theta) / sin_theta_0
    return (s0 * q0) + (s1 * q1)

# Quaternion rotation
def quat_rotate(q, v):
    qw, qx, qy, qz = q
    t = 2.0 * np.cross([qx, qy, qz], v)
    return v + qw*t + np.cross([qx, qy, qz], t)

# Payload cube and rods
def draw_payload(ax, pos, quat, scale=0.25):
    s = scale
    corners = np.array([[+s,+s,+s],[+s,+s,-s],[+s,-s,+s],[+s,-s,-s],
                        [-s,+s,+s],[-s,+s,-s],[-s,-s,+s],[-s,-s,-s]])
    world = np.array([quat_rotate(quat, c) for c in corners]) + pos
    edges = [(0,1),(0,2),(0,4),(7,6),(7,5),(7,3),(1,3),(1,5),(2,3),(2,6),(4,5),(4,6)]
    for i,j in edges:
        ax.plot([world[i,0],world[j,0]],[world[i,1],world[j,1]],[world[i,2],world[j,2]],lw=1)

    # Main body rod (centerline)
    p1 = quat_rotate(quat, np.array([s*1.6,0,0])) + pos
    p2 = quat_rotate(quat, np.array([-s*1.6,0,0])) + pos
    ax.plot([p1[0],p2[0]],[p1[1],p2[1]],[p1[2],p2[2]],lw=2,color='black')

    # Control rod direction indicator(s)
    control_dirs = [
        np.array([0,0,1]),   # along +Z (body up)
        np.array([0,1,0]),   # along +Y (side)
    ]
    for d in control_dirs:
        v_world = quat_rotate(quat, d * ROD_LENGTH)
        arrow_end = pos + v_world
        ax.plot([pos[0], arrow_end[0]],
                [pos[1], arrow_end[1]],
                [pos[2], arrow_end[2]],
                color=ROD_COLOR, lw=2, alpha=ROD_ALPHA)

def interpolate_df(df, target_fps, real_fps):
    t_real = df.time.values
    t_interp = np.arange(t_real[0], t_real[-1], 1.0/target_fps)
    rows = []

    for ti in t_interp:
        j = np.searchsorted(t_real, ti)
        if j == 0:
            row = df.iloc[0]
        elif j >= len(df):
            row = df.iloc[-1]
        else:
            t0, t1 = t_real[j-1], t_real[j]
            alpha = (ti - t0) / (t1 - t0)
            r0, r1 = df.iloc[j-1], df.iloc[j]
            pos = (1-alpha)*r0[['px','py','pz']].to_numpy() + alpha*r1[['px','py','pz']].to_numpy()
            quat = quat_slerp(r0[['qw','qx','qy','qz']].to_numpy(),
                              r1[['qw','qx','qy','qz']].to_numpy(), alpha)
            roll  = (1-alpha)*r0.roll + alpha*r1.roll
            pitch = (1-alpha)*r0.pitch + alpha*r1.pitch
            yaw   = (1-alpha)*r0.yaw + alpha*r1.yaw
            row = {
                'time': ti, 'px': pos[0], 'py': pos[1], 'pz': pos[2],
                'qw': quat[0], 'qx': quat[1], 'qy': quat[2], 'qz': quat[3],
                'roll': roll, 'pitch': pitch, 'yaw': yaw
            }
        rows.append(row)
    return pd.DataFrame(rows)

def render(df, out_path, fps):
    bbox_min = df[['px','py','pz']].min().values
    bbox_max = df[['px','py','pz']].max().values
    center = (bbox_min + bbox_max)/2
    span = (bbox_max - bbox_min).max() + 1.0

    ff = start_ffmpeg(out_path, fps)
    fig = plt.figure(figsize=(14,6))
    gs = fig.add_gridspec(1,2,width_ratios=[2,1],wspace=0.15)
    ax3 = fig.add_subplot(gs[0], projection='3d')
    ax2 = fig.add_subplot(gs[1])

    try:
        for i, row in tqdm(df.iterrows(), total=len(df), desc="Render w/ control rods"):
            pos = np.array([row.px, row.py, row.pz])
            quat = row[['qw','qx','qy','qz']].to_numpy()

            ax3.cla(); ax2.cla()
            ax3.set_xlim(center[0]-span/2, center[0]+span/2)
            ax3.set_ylim(center[1]-span/2, center[1]+span/2)
            ax3.set_zlim(center[2]-span/2, center[2]+span/2)
            ax3.plot(df.px[:i+1], df.py[:i+1], df.pz[:i+1], lw=1, alpha=0.7)
            draw_payload(ax3, pos, quat, scale=0.25)
            ax3.set_title(f"t={row.time:.2f}s | alt={row.pz:.1f} m")

            t = df.time.values
            ax2.plot(t, np.rad2deg(df.roll), label='roll')
            ax2.plot(t, np.rad2deg(df.pitch), label='pitch')
            ax2.plot(t, np.rad2deg(df.yaw), label='yaw')
            ax2.axvline(row.time, color='k', lw=0.8)
            ax2.set_xlim(t[0], t[-1]); ax2.legend(fontsize=8)
            ax2.set_xlabel("Time (s)"); ax2.set_ylabel("°")

            fig.tight_layout()
            buf = io.BytesIO(); fig.canvas.print_png(buf)
            ff.stdin.write(buf.getvalue()); buf.close()

        ff.stdin.close()
        _, stderr = ff.communicate()
        if ff.returncode != 0:
            raise RuntimeError(stderr.decode())
        print("✅ Render complete:", out_path)
    finally:
        plt.close(fig)
        if ff.poll() is None: ff.kill()

if __name__ == "__main__":
    df = pd.read_csv(DATA_CSV)
    df_i = interpolate_df(df, TARGET_FPS, REAL_FPS)
    os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)
    render(df_i, OUT_MP4, TARGET_FPS)
