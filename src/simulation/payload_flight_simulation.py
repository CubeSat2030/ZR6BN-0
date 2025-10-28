import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

# --- 1. MOCK DATA GENERATION (Simulating an Unstable Flight) ---
# NOTE: This section generates synthetic data. When you have your actual log file,
# you will replace this function with code that loads and formats your real MPU6050 data.

def generate_mock_data(flight_time_seconds, sample_rate_hz=20):
    """
    Generates synthetic MPU6050 data simulating a noisy, unstable HAB flight.

    The simulated flight includes:
    - A gentle, periodic swing in pitch and roll (simulating tether dynamics).
    - Random noise typical of a real IMU.
    """
    dt = 1.0 / sample_rate_hz
    num_steps = int(flight_time_seconds * sample_rate_hz)
    time = np.linspace(0, flight_time_seconds, num_steps)

    print(f"Generating mock data for {flight_time_seconds} seconds ({num_steps} samples)...")

    # Base disturbance (simulating an unstable, swaying payload)
    base_roll = 10 * np.sin(time / 10)  # Slow roll oscillation (max 10 degrees)
    base_pitch = 15 * np.cos(time / 8) # Slower pitch oscillation (max 15 degrees)

    # Convert base attitudes to radians for physics calculations
    base_roll_rad = np.deg2rad(base_roll)
    base_pitch_rad = np.deg2rad(base_pitch)

    # 1. Angular Velocity (Gyroscope Data)
    # Angular velocity is the derivative of the base attitude, plus noise
    # Simple differencing is used here for mock data creation
    roll_rate = np.diff(base_roll_rad, prepend=base_roll_rad[0]) / dt
    pitch_rate = np.diff(base_pitch_rad, prepend=base_pitch_rad[0]) / dt

    # Simulate a drift in Yaw (common for gyros without magnetometer correction)
    yaw_rate = np.ones(num_steps) * 0.005 + 0.01 * np.sin(time/5)

    # Add Gyro Noise (e.g., 0.02 rad/s standard deviation)
    gyro_noise = np.random.normal(0, 0.02, (num_steps, 3))

    # Raw Angular Rate (rad/s)
    raw_w = np.column_stack([
        roll_rate,
        pitch_rate,
        yaw_rate
    ]) + gyro_noise

    # 2. Acceleration (Accelerometer Data)
    # In a stable flight, acceleration is dominated by gravity (9.81 m/s^2)
    g = 9.81 # m/s^2

    # Rotate the gravity vector [0, 0, g] by the base attitude (Roll and Pitch)
    # This simulates how the MPU6050 'sees' gravity when the payload tilts.
    raw_a = np.zeros((num_steps, 3))
    for i in range(num_steps):
        r_rot = R.from_euler('zyx', [0, base_pitch_rad[i], base_roll_rad[i]], degrees=False)
        # Gravity vector in body frame (Accel reading is opposite of gravity direction)
        gravity_in_body_frame = r_rot.apply([0, 0, g])

        # Add linear acceleration components (e.g., from wind buffeting)
        linear_accel = np.array([0.5 * np.sin(time[i]), 0.5 * np.cos(time[i]), 0.1 * np.random.randn()])

        # Raw Acceleration (m/s^2)
        raw_a[i] = -gravity_in_body_frame + linear_accel

    # Add Accel Noise (e.g., 0.05 m/s^2 standard deviation)
    raw_a += np.random.normal(0, 0.05, (num_steps, 3))

    return time, raw_w, raw_a, dt

# --- 2. ATTITUDE ESTIMATION (Complementary Filter for "Actual Flight Path") ---

def complementary_filter(raw_w, raw_a, dt, alpha=0.98):
    """
    Estimates the payload's roll and pitch history using a Complementary Filter.
    This gives us the ACTUAL flight disturbance to feed into the dynamics model.
    """
    num_steps = raw_w.shape[0]
    roll_history = np.zeros(num_steps)
    pitch_history = np.zeros(num_steps)

    for i in range(1, num_steps):
        # 1. Integration (Gyroscope)
        # Use previous fused angle and current angular velocity
        roll_gyro = roll_history[i-1] + raw_w[i, 0] * dt
        pitch_gyro = pitch_history[i-1] + raw_w[i, 1] * dt

        # 2. Correction (Accelerometer)
        # Roll from Accel: atan2(Ay, Az)
        roll_accel = np.arctan2(raw_a[i, 1], raw_a[i, 2])

        # Pitch from Accel: atan2(-Ax, sqrt(Ay^2 + Az^2))
        pitch_accel = np.arctan2(-raw_a[i, 0], np.sqrt(raw_a[i, 1]**2 + raw_a[i, 2]**2))

        # 3. Fusion: High-pass Gyro (alpha) + Low-pass Accel (1-alpha)
        roll_history[i] = alpha * roll_gyro + (1 - alpha) * roll_accel
        pitch_history[i] = alpha * pitch_gyro + (1 - alpha) * pitch_accel

    # Return attitudes in radians and angular rates (used as disturbance input)
    return np.column_stack([roll_history, pitch_history, np.zeros(num_steps)]), raw_w

# --- 3. ROTATIONAL DYNAMICS MODEL ---

def rotational_dynamics(dt, attitude_q, moments_total, I, w):
    """
    Models the rotational motion of the rigid-body payload (Euler's Equations).

    w_dot = I^-1 * (Moments - w x (I * w))
    
    This function updates the angular velocity (w) and attitude (attitude_q) 
    based on the total moments applied over a time step (dt).
    """

    # I * w term (inertia times angular velocity)
    Iw = I @ w

    # w x (I * w) term (Gyroscopic Moment)
    w_cross_Iw = np.cross(w, Iw)

    # w_dot calculation (Angular Acceleration)
    w_dot = np.linalg.inv(I) @ (moments_total - w_cross_Iw)

    # 1. Update Angular Velocity (w) using Euler integration
    w_new = w + w_dot * dt

    # 2. Update Attitude (Quaternion)
    angle = np.linalg.norm(w_new * dt)
    if angle > 1e-6:
        axis = w_new / np.linalg.norm(w_new)
        delta_rotation = R.from_rotvec(axis * angle)

        current_rotation = R.from_quat(attitude_q)
        # Apply the delta rotation (passive rotation)
        new_rotation = delta_rotation * current_rotation
        attitude_q_new = new_rotation.as_quat()
    else:
        attitude_q_new = attitude_q # No change if angular velocity is negligible

    return attitude_q_new, w_new

# --- 4. MAIN SIMULATION ENGINE ---

def simulate_control_system(flight_time=300):
    """
    Main simulation loop that runs the HAB data through the vector control model.
    """

    # --- A. Setup and Data Preprocessing ---
    time, raw_w, raw_a, dt = generate_mock_data(flight_time)
    attitude_rad_actual, w_disturbance_rad_actual = complementary_filter(raw_w, raw_a, dt)

    num_steps = len(time)

    # --- B. Control & Payload Parameters ---

    # Target Attitude (The goal of the vector control system)
    TARGET_ATTITUDE_EULER = np.deg2rad([0.0, 0.0, 0.0]) # Level flight

    # Payload Inertia (MASS PROPERTIES ARE CRITICAL - REPLACE WITH YOUR VALUES)
    # I = [[Ixx, 0, 0], [0, Iyy, 0], [0, 0, Izz]] (Moment of Inertia Matrix)
    I = np.diag([0.15, 0.15, 0.1]) # Example: 0.15 kg*m^2 for Roll and Pitch

    # PID Gains for the Vector Control System (These must be tuned!)
    Kp = 15.0  # Proportional Gain (Response to current error)
    Ki = 0.5   # Integral Gain (Eliminates steady-state error/drift)
    Kd = 10.0  # Derivative Gain (Damping/Response to rate of error change)

    # --- C. Simulation State Variables ---
    attitude_q_history = np.zeros((num_steps, 4))
    angular_rate_history = np.zeros((num_steps, 3))
    control_moment_history = np.zeros((num_steps, 3))

    # Control loop states
    integral_error = np.zeros(3)

    # Initial Conditions (Using the first measurement from the complementary filter)
    r0 = R.from_euler('xyz', attitude_rad_actual[0, :], degrees=False)
    current_attitude_q = r0.as_quat()
    current_angular_rate = raw_w[0, :]

    attitude_q_history[0] = current_attitude_q
    angular_rate_history[0] = current_angular_rate

    print("\nStarting Control System Simulation...")

    # --- D. Main Simulation Loop ---
    for i in range(1, num_steps):
        # 1. Calculate Error
        r_current = R.from_quat(current_attitude_q)
        current_euler = r_current.as_euler('xyz', degrees=False) # [Roll, Pitch, Yaw]

        # Attitude Error (Target - Current)
        error = TARGET_ATTITUDE_EULER - current_euler

        # Rate of Change of Error (Derivative term) - Assuming target rate is zero
        derivative_error = -current_angular_rate

        # Accumulate Integral Error
        integral_error += error * dt

        # 2. Calculate Control Moment (M_control)
        M_control = (
            Kp * error +
            Ki * integral_error +
            Kd * derivative_error
        )

        # 3. Apply Total Moments to Dynamics Model

        # Disturbance Moment (M_disturbance): The moment that *caused* the actual flight data.
        # This is a critical simplification: we estimate the external moment by scaling 
        # the observed angular rate from the flight data.
        M_disturbance = w_disturbance_rad_actual[i] * 1.5 * np.max(I)

        # Total Moment (Control + Disturbance)
        M_total = M_control + M_disturbance

        # 4. Propagate Dynamics
        current_attitude_q, current_angular_rate = rotational_dynamics(
            dt,
            current_attitude_q,
            M_total,
            I,
            current_angular_rate
        )

        # 5. Store Results
        attitude_q_history[i] = current_attitude_q
        angular_rate_history[i] = current_angular_rate
        control_moment_history[i] = M_control

    print("Simulation complete. Generating visualization.")

    # --- E. Visualization (Plotting Results) ---

    # Convert quaternions back to Euler angles for plotting (degrees)
    r_simulated = R.from_quat(attitude_q_history)
    attitude_deg_simulated = r_simulated.as_euler('xyz', degrees=True)

    # Convert actual data (from complementary filter) to degrees
    attitude_deg_actual = np.rad2deg(attitude_rad_actual)

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('HAB Payload Vector Control Simulation', fontsize=16, weight='bold')

    # --- Plot 1: Attitude Stabilization (Roll) ---
    ax1.plot(time, attitude_deg_actual[:, 0], label='Actual Flight Roll (Disturbance)', color='#2c3e50', alpha=0.6)
    ax1.plot(time, attitude_deg_simulated[:, 0], label='Simulated Controlled Roll', color='#e74c3c', linewidth=2)
    ax1.hlines(0, time[0], time[-1], color='gray', linestyle='--', alpha=0.7)
    ax1.set_title('Roll Angle (X-Axis) Stabilization', fontsize=12)
    ax1.set_ylabel('Angle (degrees)')
    ax1.legend(loc='upper right')
    ax1.grid(True)

    # --- Plot 2: Attitude Stabilization (Pitch) ---
    ax2.plot(time, attitude_deg_actual[:, 1], label='Actual Flight Pitch (Disturbance)', color='#2c3e50', alpha=0.6)
    ax2.plot(time, attitude_deg_simulated[:, 1], label='Simulated Controlled Pitch', color='#3498db', linewidth=2)
    ax2.hlines(0, time[0], time[-1], color='gray', linestyle='--', alpha=0.7)
    ax2.set_title('Pitch Angle (Y-Axis) Stabilization', fontsize=12)
    ax2.set_ylabel('Angle (degrees)')
    ax2.legend(loc='upper right')
    ax2.grid(True)

    # --- Plot 3: Control Moment Output ---
    ax3.plot(time, control_moment_history[:, 0], label='Roll Control Moment ($M_x$)', color='#f39c12')
    ax3.plot(time, control_moment_history[:, 1], label='Pitch Control Moment ($M_y$)', color='#27ae60')
    ax3.set_title('Required Control Moment from Vector Actuator', fontsize=12)
    ax3.set_xlabel('Time (seconds)')
    ax3.set_ylabel('Moment (Nm)')
    ax3.legend(loc='upper right')
    ax3.grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

if __name__ == '__main__':
    # Run the simulation for 300 seconds of flight data
    simulate_control_system(flight_time=300)

    print("\nScript execution finished. Check the generated plots for results.")
    print("------------------------------------------------------------------")
