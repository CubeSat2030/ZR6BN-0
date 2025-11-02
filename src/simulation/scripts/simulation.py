import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import time
import os

# --- Configuration ---
# Set the base directory relative to the script location
SCRIPT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')
DATA_FILE_PATH = os.path.join(BASE_DIR, 'src', 'logger', 'data', 'MPU6050.txt')

# --- 1. Data Parsing & Orientation Calculation ---

def load_and_process_data(file_path):
    """
    Reads MPU6050 data and calculates Euler angles (Roll, Pitch, Yaw)
    from the angular velocity (gyroscope) readings.
    
    MPU6050.txt is assumed to have data rows like:
    [Time_ms], [Ax], [Ay], [Az], [Gx], [Gy], [Gz], ...
    Where Gx, Gy, Gz are angular velocities (rad/s or deg/s).
    We'll assume 'deg/s' and a fixed sample rate (dt).
    
    NOTE: A simple integration (summation) will cause drift. 
    A real-world HAB would use a **Complementary Filter** or **Kalman Filter** combining both accelerometer and gyroscope data to calculate accurate orientation.
    """
    
    print(f"Loading data from: {file_path}")
    
    # Placeholder for the data columns we need: Time, Gx, Gy, Gz
    # Assuming Gx, Gy, Gz are columns 5, 6, 7 (index 4, 5, 6)
    try:
        # Load columns assuming they are space or comma separated
        data = np.loadtxt(file_path, delimiter=',') 
    except FileNotFoundError:
        print(f"ERROR: Data file not found at {file_path}")
        return None, None
    except ValueError:
        print("ERROR: Data format error. Ensure the MPU6050 data is numeric and separated correctly.")
        return None, None
        
    # Assuming the following column order (adjust if needed):
    # Time (s), Ax, Ay, Az, Gx (Roll Rate), Gy (Pitch Rate), Gz (Yaw Rate)
    # Get Gyro rates (assuming columns 4, 5, 6 correspond to Gx, Gy, Gz)
    try:
        time_data = data[:, 0]
        gyro_rates = data[:, 4:7] # Gx, Gy, Gz in deg/s
    except IndexError:
        print("ERROR: Data file does not have enough columns (expecting at least 7).")
        return None, None

    # Calculate time step (dt)
    dt_samples = np.diff(time_data)
    # Use the median time step, or assume a fixed one if file doesn't have time
    dt = np.median(dt_samples) if len(dt_samples) > 0 else 0.01  # Default to 10ms
    
    # Simple Numerical Integration (Euler Integration) to get angles
    # Angles = cumulative sum of (rate * dt)
    roll = np.cumsum(gyro_rates[:, 0] * dt) # Roll = integral of Gx
    pitch = np.cumsum(gyro_rates[:, 1] * dt) # Pitch = integral of Gy
    yaw = np.cumsum(gyro_rates[:, 2] * dt) # Yaw = integral of Gz
    
    # Convert from degrees to radians for trigonometric functions
    roll_rad = np.deg2rad(roll)
    pitch_rad = np.deg2rad(pitch)
    yaw_rad = np.deg2rad(yaw)
    
    orientation_data = np.vstack([roll_rad, pitch_rad, yaw_rad]).T
    
    return orientation_data, time_data

# --- 2. 3D Cube Definition ---

def get_cube_vertices(scale=1.0):
    """Define the vertices of a unit cube centered at the origin."""
    v = np.array([
        [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],
        [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1]
    ])
    # Scale and make it half size for unit cube to fit easily in plot
    return v * scale / 2.0 

def get_cube_faces():
    """Define the faces (triangles) that make up the cube."""
    return [
        [0, 1, 2, 3], [4, 5, 6, 7], # Back and Front
        [0, 1, 5, 4], [2, 3, 7, 6], # Bottom and Top
        [1, 2, 6, 5], [4, 7, 3, 0]  # Right and Left
    ]

# --- 3. Rotation Logic (Applying Roll, Pitch, Yaw) ---

def rotate_cube(vertices, roll, pitch, yaw):
    """Applies rotation matrices for Roll (X), Pitch (Y), and Yaw (Z) to the vertices."""
    
    # Roll Rotation Matrix (X-axis)
    R_roll = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    # Pitch Rotation Matrix (Y-axis)
    R_pitch = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    # Yaw Rotation Matrix (Z-axis)
    R_yaw = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    # Combine rotations (order matters: R = R_yaw * R_pitch * R_roll)
    R = np.dot(R_yaw, np.dot(R_pitch, R_roll))
    
    # Apply rotation to all vertices
    rotated_vertices = np.dot(vertices, R.T)
    return rotated_vertices

# --- 4. Matplotlib Animation ---

def animate_payload(i, orientation_data, cube_plot):
    """
    Updates the cube's position and orientation for the animation frame 'i'.
    """
    if i >= len(orientation_data):
        return cube_plot # Stop the animation when data runs out
        
    roll, pitch, yaw = orientation_data[i]
    
    # 1. Rotate the base cube
    base_vertices = get_cube_vertices(scale=2)
    rotated_vertices = rotate_cube(base_vertices, roll, pitch, yaw)
    
    # 2. Update the cube's vertices in the plot (Matplotlib requires a special update)
    # The cube faces are defined by polygons (Poly3DCollection).
    
    # This is complex in Matplotlib. For simplicity with the limited API:
    # We will just re-draw the cube's bounding box or line segments for each frame.
    
    # Clear the previous plot and re-draw the cube's edges (simpler approach)
    ax = cube_plot[0].axes
    ax.clear()
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    ax.set_title(f'HAB Payload Orientation (Frame: {i+1})')
    
    # Draw the rotated cube's edges
    faces = get_cube_faces()
    for face in faces:
        x = [rotated_vertices[v][0] for v in face + [face[0]]] # Close the loop
        y = [rotated_vertices[v][1] for v in face + [face[0]]]
        z = [rotated_vertices[v][2] for v in face + [face[0]]]
        ax.plot(x, y, z, color='b')

    # Draw a prominent axis on the cube to show orientation (e.g., the "nose")
    # Z-axis line from center to (0,0,1)
    nose_vector = np.array([0, 0, 1.5]) 
    rotated_nose = np.dot(nose_vector, rotate_cube(np.identity(3), roll, pitch, yaw))

    ax.plot([0, rotated_nose[0][2]], [0, rotated_nose[1][2]], [0, rotated_nose[2][2]], color='r', linewidth=3)
    
    return cube_plot

def run_simulation():
    # Load and process data
    orientation_data, time_data = load_and_process_data(DATA_FILE_PATH)
    if orientation_data is None:
        return

    # --- Setup 3D Plot ---
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("HAB Payload MPU6050 3D Orientation Simulation 🛰️")
    ax.set_xlabel("X-Axis (Roll)")
    ax.set_ylabel("Y-Axis (Pitch)")
    ax.set_zlabel("Z-Axis (Yaw)")
    
    # Set limits for the plot to keep the cube centered and visible
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    
    # Initial draw of the cube (placeholder for the FuncAnimation update)
    # Matplotlib's Poly3DCollection is complex to update, so we use a list of lines/plots.
    # We pass an empty list of plots to the animation, and `animate_payload` will clear and redraw.
    initial_cube_plot = [ax.plot([0],[0],[0], color='b')[0]] # Dummy plot element
    
    # Calculate the interval for the animation based on the median time step
    if time_data is not None and len(time_data) > 1:
        # Time data is in seconds, convert the median delta time to milliseconds
        # for the animation interval.
        median_dt_ms = np.median(np.diff(time_data)) * 1000 
    else:
        median_dt_ms = 10.0 # Default to 10ms refresh rate

    # Create the animation
    ani = FuncAnimation(
        fig, 
        animate_payload, 
        fargs=(orientation_data, initial_cube_plot),
        frames=len(orientation_data),
        interval=median_dt_ms, 
        repeat=False
    )

    plt.show()

if __name__ == '__main__':
    run_simulation()