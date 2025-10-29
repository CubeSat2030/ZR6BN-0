#!/usr/bin/env python3
"""
render_stream.py
- Streams Matplotlib PNG frames to ffmpeg via stdin (image2pipe).
- Keeps video duration == flight duration by using FPS == sample rate.
- No intermediate PNG files written to disk.

Requirements:
- ffmpeg installed and on PATH
- Python packages: numpy, pandas, matplotlib, tqdm

Usage:
python scripts/render_stream.py
"""
import os
import io
import shlex
import subprocess
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # offscreen backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 import for 3D projection

# CONFIG
DATA_CSV = "../data/trajectory.csv"
FUTURE_CSV = "../out/video/future_last.csv"
OUT_DIR = "../out/video"
OUT_MP4 = os.path.join(OUT_DIR, "hab_sim_stream.mp4")
FPS = 10  # default; set to your sample rate (10 Hz typical)
CRF = 18
PRESET = "medium"
FFMPEG_LOGLEVEL = "error"  # set to "info" for more ffmpeg output

os.makedirs(OUT_DIR, exist_ok=True)

# -- helpers ---------------------------------------------------------------
def start_ffmpeg_process(out_path, fps=FPS, crf=CRF, preset=PRESET):
    # ffmpeg command to read PNGs from stdin (image2pipe)
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "image2pipe",
        "-vcodec", "png",
        "-r", str(fps),
        "-i", "-",                   # input from stdin
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        out_path
    ]
    # Launch
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc

def quat_rotate_vector(q, v):
    # q = [qw, qx, qy, qz], rotate v (body->world)
    qw, qx, qy, qz = q
    t = 2.0 * np.cross([qx, qy, qz], v)
    return v + qw * t + np.cross([qx, qy, qz], t)

def draw_payload(ax3, pos, quat, scale=0.25):
    s = scale
    corners = np.array([[+s,+s,+s],[+s,+s,-s],[+s,-s,+s],[+s,-s,-s],
                        [-s,+s,+s],[-s,+s,-s],[-s,-s,+s],[-s,-s,-s]])
    def qrot(q, v):
        qw,qx,qy,qz = q
        t = 2*np.cross([qx,qy,qz], v)
        return v + qw*t + np.cross([qx,qy,qz], t)
    world_c = np.array([qrot(quat, c) for c in corners]) + pos
    edges = [(0,1),(0,2),(0,4),(7,6),(7,5),(7,3),(1,3),(1,5),(2,3),(2,6),(4,5),(4,6)]
    for (i,j) in edges:
        ax3.plot([world_c[i,0], world_c[j,0]],
                 [world_c[i,1], world_c[j,1]],
                 [world_c[i,2], world_c[j,2]], linewidth=1)
    # rod along body x-axis
    p1 = qrot(quat, np.array([s*1.6,0,0])) + pos
    p2 = qrot(quat, np.array([-s*1.6,0,0])) + pos
    ax3.plot([p1[0],p2[0]],[p1[1],p2[1]],[p1[2],p2[2]], linewidth=2)

# -- rendering pipeline ----------------------------------------------------
def render_stream(data_csv=DATA_CSV, future_csv=FUTURE_CSV, out_mp4=OUT_MP4, fps=FPS):
    df = pd.read_csv(data_csv)
    future = pd.read_csv(future_csv)
    n = len(df)
    if n == 0:
        raise RuntimeError("No frames to render (empty trajectory).")

    # Precompute bounding box (global) for consistent framing
    bbox_min = df[['px','py','pz']].min().values
    bbox_max = df[['px','py','pz']].max().values
    center = (bbox_min + bbox_max) / 2.0
    max_span = max( (bbox_max - bbox_min).max(), 1.0 ) + 1.0

    # Start ffmpeg
    print(f"Starting ffmpeg -> {out_mp4}")
    ff = start_ffmpeg_process(out_mp4, fps=fps, crf=CRF, preset=PRESET)

    # We'll create a single figure and reuse it to avoid repeated allocations
    fig = plt.figure(figsize=(14,6))
    gs = fig.add_gridspec(1,2, width_ratios=[2,1], wspace=0.15)
    ax3 = fig.add_subplot(gs[0], projection='3d')
    ax2 = fig.add_subplot(gs[1])

    try:
        for i in tqdm(range(n), desc="Rendering frames", unit="frame"):
            row = df.iloc[i]
            pos = np.array([row.px, row.py, row.pz])
            quat = row[['qw','qx','qy','qz']].to_numpy()

            # Clear axes
            ax3.cla()
            ax2.cla()

            # 3D axes limits & labels
            ax3.set_xlim(center[0]-max_span/2, center[0]+max_span/2)
            ax3.set_ylim(center[1]-max_span/2, center[1]+max_span/2)
            zlow = max(0.0, center[2]-max_span/2)
            ax3.set_zlim(zlow, center[2]+max_span/2)
            ax3.set_xlabel("X (m)")
            ax3.set_ylabel("Y (m)")
            ax3.set_zlabel("Z (m)")

            # Past trail
            past = df.iloc[:i+1]
            ax3.plot(past.px, past.py, past.pz, linewidth=1, alpha=0.7)

            # Future points (use entire precomputed future for simplicity)
            if not future.empty:
                ax3.scatter(future.fx, future.fy, future.fz, s=6, marker='o', alpha=0.5)

            # Draw payload at current pose
            draw_payload(ax3, pos, quat, scale=0.25)
            ax3.set_title(f"Time: {row.time:.1f}s  |  Alt: {row.pz:.1f} m")

            # Telemetry plot (roll/pitch/yaw)
            t = df.time.values
            ax2.plot(t, np.rad2deg(df.roll), label='roll', linewidth=1)
            ax2.plot(t, np.rad2deg(df.pitch), label='pitch', linewidth=1)
            ax2.plot(t, np.rad2deg(df.yaw), label='yaw', linewidth=1)
            ax2.axvline(row.time, color='k')
            ax2.set_xlim(t[0], t[-1])
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("deg")
            ax2.legend(loc='upper left', fontsize=8)

            fig.tight_layout()

            # Render to PNG in memory
            buf = io.BytesIO()
            fig.canvas.print_png(buf)
            png_bytes = buf.getvalue()

            # Write PNG bytes to ffmpeg stdin
            try:
                ff.stdin.write(png_bytes)
            except BrokenPipeError:
                raise RuntimeError("ffmpeg pipe closed unexpectedly. See ffmpeg stderr for details.")

            # small cleanup
            buf.close()

        # finish
        ff.stdin.close()
        stdout, stderr = ff.communicate()
        if ff.returncode != 0:
            err_text = stderr.decode('utf-8', errors='ignore') if isinstance(stderr, bytes) else str(stderr)
            raise RuntimeError(f"ffmpeg failed with return code {ff.returncode}:\n{err_text}")
        print("Rendering complete:", out_mp4)

    finally:
        plt.close(fig)
        if ff.poll() is None:
            ff.kill()

if __name__ == "__main__":
    render_stream()
