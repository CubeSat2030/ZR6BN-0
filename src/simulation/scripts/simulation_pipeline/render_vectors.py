#!/usr/bin/env python3
"""
render_vectors.py
---------------------------------
3D cinematic replay of HAB payload flight with control rod direction indicators.

Reads:  src/simulation/output/data/trajectory.csv
Outputs: src/media/output/video/hab_sim_control_vectors.mp4
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
from pathlib import Path

INPUT = Path("src/simulation/output/data/trajectory.csv")
OUTPUT = Path("src/media/output/video/hab_sim_control_vectors.mp4")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def render_simulation():
    df = pd.read_csv(INPUT)
    fps = 30
    interval = 1 / fps

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_zlim(0, 10)
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.set_title("HAB Payload Flight — Vector Visualization")

    payload, = ax.plot([], [], [], 'o', color='gold', markersize=8)
    rod, = ax.plot([], [], [], color='cyan', linewidth=2)

    writer = FFMpegWriter(fps=fps, metadata=dict(artist="Nathan Busse"))

    with writer.saving(fig, str(OUTPUT), dpi=150):
        for _, row in df.iterrows():
            pos = np.array([row.px, row.py, row.pz])
            rot = R.from_quat([row.qx, row.qy, row.qz, row.qw])
            fwd = rot.apply([0, 0, 1])
            rod_len = 0.6

            rod_start = pos
            rod_end = pos + fwd * rod_len

            payload.set_data([pos[0]], [pos[1]])
            payload.set_3d_properties([pos[2]])
            rod.set_data([rod_start[0], rod_end[0]], [rod_start[1], rod_end[1]])
            rod.set_3d_properties([rod_start[2], rod_end[2]])

            writer.grab_frame()

    print(f"[🎥] Render complete → {OUTPUT}")

if __name__ == "__main__":
    render_simulation()
