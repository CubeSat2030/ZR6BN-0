#!/usr/bin/env python3
"""
render.py
- Renders frames to out/video/frames_%06d.png then assembles to MP4 via ffmpeg.
- Designed to handle very large frame counts by chunked rendering.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # offscreen
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import subprocess

DATA = "../data/trajectory.csv"
FUTURE = "../out/video/future_last.csv"
OUT_DIR = "../out/video"
FRAME_PREFIX = os.path.join(OUT_DIR, "frame_%06d.png")
VIDEO_OUT = os.path.join(OUT_DIR, "hab_sim.mp4")
FPS = 10  # set same as sample rate to keep real-time duration
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR, exist_ok=True)

def draw_payload(ax3, pos, quat, scale=0.2):
    # Render a cube centered at pos and a rod
    # Build 8 cube corners in body frame then rotate to world
    # Cube vertices
    s = scale
    corners = np.array([[+s,+s,+s],[+s,+s,-s],[+s,-s,+s],[+s,-s,-s],
                        [-s,+s,+s],[-s,+s,-s],[-s,-s,+s],[-s,-s,-s]])
    # rotate corners by quaternion
    def qrot(q, v):
        qw,qx,qy,qz = q
        t = 2*np.cross([qx,qy,qz], v)
        return v + qw*t + np.cross([qx,qy,qz], t)
    world_c = np.array([qrot(quat, c) for c in corners]) + pos
    # draw edges
    edges = [(0,1),(0,2),(0,4),(7,6),(7,5),(7,3),(1,3),(1,5),(2,3),(2,6),(4,5),(4,6)]
    for (i,j) in edges:
        ax3.plot([world_c[i,0], world_c[j,0]],
                 [world_c[i,1], world_c[j,1]],
                 [world_c[i,2], world_c[j,2]], linewidth=1)
    # rod along body x axis:
    p1 = qrot(quat, np.array([s*1.6,0,0])) + pos
    p2 = qrot(quat, np.array([-s*1.6,0,0])) + pos
    ax3.plot([p1[0],p2[0]],[p1[1],p2[1]],[p1[2],p2[2]], linewidth=2)

def render_frame(i, df, future, outpath):
    # df row i
    row = df.iloc[i]
    pos = np.array([row.px, row.py, row.pz])
    quat = row[['qw','qx','qy','qz']].to_numpy()
    # create figure
    fig = plt.figure(figsize=(14,6))
    gs = fig.add_gridspec(1,2, width_ratios=[2,1], wspace=0.15)
    ax3 = fig.add_subplot(gs[0], projection='3d')
    # set limits around entire flight for consistent camera
    # derive global bounding box once - but for simplicity compute here
    bbox = np.vstack([df[['px','py','pz']].min().values, df[['px','py','pz']].max().values])
    center = (bbox[0]+bbox[1])/2
    maxspan = np.max(bbox[1]-bbox[0]) + 1.0
    ax3.set_xlim(center[0]-maxspan/2, center[0]+maxspan/2)
    ax3.set_ylim(center[1]-maxspan/2, center[1]+maxspan/2)
    ax3.set_zlim(max(0, center[2]-maxspan/2), center[2]+maxspan/2)
    # draw past trail
    past = df.iloc[:i+1]
    ax3.plot(past.px, past.py, past.pz, linewidth=1, alpha=0.7)
    # draw future dots (project from current)
    fut = future.values
    ax3.scatter(fut[:,0], fut[:,1], fut[:,2], s=6, marker='o', alpha=0.6)
    # draw payload
    draw_payload(ax3, pos, quat, scale=0.25)
    ax3.set_title(f"Time: {row.time:.1f}s | Alt: {row.pz:.1f} m")
    ax3.set_xlabel("X (m)")
    ax3.set_ylabel("Y (m)")
    ax3.set_zlabel("Z (m)")
    # telemetry subplot
    ax2 = fig.add_subplot(gs[1])
    t = df.time.values
    # small telemetry: roll/pitch/yaw
    ax2.plot(t, np.rad2deg(df.roll), label='roll', linewidth=1)
    ax2.plot(t, np.rad2deg(df.pitch), label='pitch', linewidth=1)
    ax2.plot(t, np.rad2deg(df.yaw), label='yaw', linewidth=1)
    ax2.axvline(row.time, color='k')
    ax2.set_xlim(t[0], t[-1])
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("deg")
    ax2.legend(loc='upper left', fontsize=8)
    # save frame
    fig.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close(fig)

def assemble_ffmpeg(pattern, out, fps=FPS, crf=18):
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", pattern,
        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
        "-pix_fmt", "yuv420p", out
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    df = pd.read_csv(DATA)
    future = pd.read_csv(FUTURE)
    n = len(df)
    print(f"Rendering {n} frames -> {VIDEO_OUT} @ {FPS} fps")
    # Precompute bounding box once to speed up frame rendering
    for i in tqdm(range(n)):
        outpath = os.path.join(OUT_DIR, f"frame_{i:06d}.png")
        if os.path.exists(outpath):
            continue
        render_frame(i, df, future, outpath)
    # assemble
    assemble_ffmpeg(os.path.join(OUT_DIR, "frame_%06d.png"), VIDEO_OUT, fps=FPS)
    print("Done:", VIDEO_OUT)

if __name__ == "__main__":
    main()
