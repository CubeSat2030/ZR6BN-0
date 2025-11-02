import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import os

# --------------------------------------------------------------------
# --- 1. FILE PATH CONFIGURATION (THE CHANGES ARE HERE) ---
# --------------------------------------------------------------------

# !!! CHANGE THESE TWO LINES !!!
# 1. Specify the folder where your MPU6050.txt file is located
# Use a raw string (r"...") for Windows paths to avoid issues with backslashes
DATA_DIR = r"src/logger/data"  # Example: r"C:\path\to\your\data" or "/path/to/your/data"

# 2. Specify the file name
FILE_NAME = 'MPU6050.txt'

# Construct the full, cross-platform file path
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

# Skips the 10 lines of comments/headers before the data starts (line 11 is the first data row)
HEADER_LINES_TO_SKIP = 10 

# --------------------------------------------------------------------
# --- 2. DATA LOADING & CLEANING ---
# --------------------------------------------------------------------

try:
    print(f"Attempting to read data from {FILE_PATH}...")
    
    # Read the file using the constructed full path
    df = pd.read_csv(FILE_PATH, sep=',', skiprows=HEADER_LINES_TO_SKIP, skipinitialspace=True)
    
except FileNotFoundError:
    print(f"Error: The file '{FILE_PATH}' was not found.")
    print("Please check your DATA_DIR and FILE_NAME settings.")
    exit()
except Exception as e:
    print(f"An error occurred while reading or parsing the file: {e}")
    exit()

# Data Cleaning: Keep only essential columns and drop rows with missing data
essential_cols = ['velocity_m_s', 'accel_x_m_s2', 'accel_y_m_s2', 'accel_z_m_s2', 'gyro_x_rads', 'gyro_y_rads', 'gyro_z_rads']
df.replace('', np.nan, inplace=True)
df.dropna(subset=essential_cols, inplace=True)
for col in essential_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df.dropna(subset=essential_cols, inplace=True)

if df.empty:
    print("Error: DataFrame is empty after cleaning. Check file format or data content.")
    exit()

print(f"Successfully loaded {len(df)} data points.")


# --------------------------------------------------------------------
# --- 3. ATTITUDE AND TRAJECTORY ESTIMATION (Unchanged Logic) ---
# --------------------------------------------------------------------

# Constants for Complementary Filter
dt = 1.0    
alpha = 0.98 

# Initial values
roll_angle, pitch_angle, yaw_angle = 0.0, 0.0, 0.0
pos_z = 0.0

rolls, pitches, yaws, positions_z = [], [], [], []

for _, row in df.iterrows():
    ax, ay, az = row['accel_x_m_s2'], row['accel_y_m_s2'], row['accel_z_m_s2']
    gx, gy, gz = row['gyro_x_rads'], row['gyro_y_rads'], row['gyro_z_rads']

    roll_accel = np.degrees(np.arctan2(ay, az))
    pitch_accel = np.degrees(np.arctan2(-ax, np.sqrt(ay**2 + az**2)))

    roll_gyro = np.degrees(gx) * dt
    pitch_gyro = np.degrees(gy) * dt
    yaw_gyro = np.degrees(gz) * dt

    roll_angle = alpha * (roll_angle + roll_gyro) + (1 - alpha) * roll_accel
    pitch_angle = alpha * (pitch_angle + pitch_gyro) + (1 - alpha) * pitch_accel
    yaw_angle = yaw_angle + yaw_gyro

    pos_z += row['velocity_m_s'] * dt

    rolls.append(roll_angle)
    pitches.append(pitch_angle)
    yaws.append(yaw_angle)
    positions_z.append(pos_z)

df['roll_deg'] = rolls
df['pitch_deg'] = pitches
df['yaw_deg'] = yaws
df['pos_z'] = positions_z
df['pos_x'] = 0.0 
df['pos_y'] = 0.0


# --------------------------------------------------------------------
# --- 4. 3D VISUALIZATION FUNCTIONS (Unchanged Logic) ---
# --------------------------------------------------------------------

def rotation_matrix(roll, pitch, yaw):
    R_x = np.array([
        [1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]
    ])
    R_y = np.array([
        [np.cos(pitch), 0, np.sin(pitch)], [0, 1, 0], [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    R_z = np.array([
        [np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]
    ])
    return R_z @ R_y @ R_x

def plot_cube(ax, center_x, center_y, center_z, roll, pitch, yaw, size=3.0, current_index=0):
    v = np.array([
        [-0.5, -0.5, -0.5], [ 0.5, -0.5, -0.5], [ 0.5,  0.5, -0.5], [-0.5,  0.5, -0.5],
        [-0.5, -0.5,  0.5], [ 0.5, -0.5,  0.5], [ 0.5,  0.5,  0.5], [-0.5,  0.5,  0.5]
    ]) * size
    
    roll_rad, pitch_rad, yaw_rad = np.radians(roll), np.radians(pitch), np.radians(yaw)
    R = rotation_matrix(roll_rad, pitch_rad, yaw_rad)
    v_rotated = (R @ v.T).T + np.array([center_x, center_y, center_z])
    
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], 
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]
    
    ax.clear()
    
    X_grid, Y_grid = np.meshgrid(np.linspace(-5, 5, 5), np.linspace(-5, 5, 5))
    Z_grid = np.zeros_like(X_grid)
    ax.plot_surface(X_grid, Y_grid, Z_grid, alpha=0.1, color='lightblue', rstride=1, cstride=1)
    
    for edge in edges:
        p1, p2 = v_rotated[edge[0]], v_rotated[edge[1]]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'r-', linewidth=3)
        
    p1_front, p2_front = v_rotated[1], v_rotated[2]
    ax.plot([p1_front[0], p2_front[0]], [p1_front[1], p2_front[1]], [p1_front[2], p2_front[2]], 'g-', linewidth=5, label='Payload Front (X+)')

    ax.plot(df['pos_x'][:current_index+1], df['pos_y'][:current_index+1], df['pos_z'][:current_index+1], 'b--', linewidth=1)

    limit_range = 5
    ax.set_xlim([-limit_range, limit_range])
    ax.set_ylim([-limit_range, limit_range])
    
    min_z = min(df['pos_z'].min(), 0) - 5
    max_z = max(df['pos_z'].max(), 5) + 5
    ax.set_zlim([min_z, max_z])
    
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (Altitude, m)")
    
    ax.view_init(elev=20, azim=120)
    title = f"HAB Payload Simulation (Time: {current_index}s, Alt: {center_z:.2f}m)\nRoll:{roll:.1f}° Pitch:{pitch:.1f}° Yaw:{yaw:.1f}°"
    ax.set_title(title, fontsize=10)
    
    return ax.lines

# --------------------------------------------------------------------
# --- 5. ANIMATION SETUP AND EXECUTION ---
# --------------------------------------------------------------------

# Setup the figure and animation
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

animation_duration = min(60, len(df))

def animate(i):
    data_row = df.iloc[i]
    x, y, z = data_row['pos_x'], data_row['pos_y'], data_row['pos_z']
    roll, pitch, yaw = data_row['roll_deg'], data_row['pitch_deg'], data_row['yaw_deg']
    
    return plot_cube(ax, x, y, z, roll, pitch, yaw, size=3.0, current_index=i)

# Create the animation
ani = FuncAnimation(fig, animate, frames=animation_duration, interval=100, blit=False, repeat=False)

# Save and show the animation
output_path = "hab_payload_simulation.gif"
print(f"\nSaving Animation to {output_path}...")

try:
    # Requires Pillow library: pip install Pillow
    ani.save(output_path, writer='pillow', fps=10, dpi=100)
    print("Animation saved successfully! Open 'hab_payload_simulation.gif' to view it.")
    
    plt.show() 

except Exception as e:
    print(f"\nCould not save GIF. Please ensure you have the 'Pillow' library installed ('pip install Pillow').")
    print("Saving a static PNG of the final position instead.")

    final_row = df.iloc[animation_duration - 1]
    plot_cube(ax, final_row['pos_x'], final_row['pos_y'], final_row['pos_z'], 
              final_row['roll_deg'], final_row['pitch_deg'], final_row['yaw_deg'], size=3.0, current_index=animation_duration-1)
    
    static_plot_path = "hab_payload_static_plot.png"
    fig.savefig(static_plot_path)
    print(f"Static plot saved to {static_plot_path}")
    plt.close(fig)

print("\n--- Calculated Data Summary (First 5 Rows) ---")
print(df[['pos_z', 'roll_deg', 'pitch_deg', 'yaw_deg']].head().to_markdown(index=False, floatfmt=".2f"))