import subprocess
import pathlib
import sys
import time
import random
from flask import Flask, render_template, jsonify, send_from_directory, abort

# =========================================================================
# Kabot-1 Blackbox Analyzer (Refactored Web Application)
# =========================================================================
# This single Python file now manages the web interface and chart generation,
# removing the need for the separate 'blackbox.sh' script.

# --- Configuration ---
# Set the base directory to the project's root (one level up from this file's location)
BASE_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
CHARTS_DIR = SRC_DIR / "charts"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure the necessary directories exist
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Flask App Initialization ---
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

# --- Mock Plotter Functions ---
# In a real scenario, you would import your actual plotting functions from
# 'dht_plotter.py', 'mpu6050_plotter.py', etc.
# For this example, we create mock functions that generate placeholder charts.

def check_dependencies():
    """Checks for Python dependencies required for plotting."""
    try:
        import matplotlib
        import numpy
    except ImportError:
        print("Error: Missing required Python libraries.", file=sys.stderr)
        print("Please install them with: pip install matplotlib numpy", file=sys.stderr)
        return False
    return True

def generate_placeholder_chart(filename, title, x_label, y_label, color):
    """A mock function to generate a simple SVG chart using matplotlib."""
    if not check_dependencies():
        raise RuntimeError("Plotting libraries are not installed.")

    import matplotlib.pyplot as plt
    import numpy as np

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 4))

    # Generate some random data for demonstration
    x = np.linspace(0, 10, 100)
    y = np.sin(x + random.uniform(0, np.pi)) * random.uniform(0.5, 1.5) + np.random.randn(100) * 0.1

    ax.plot(x, y, color=color, linewidth=2)
    ax.set_title(title, fontsize=14, color='white', pad=15)
    ax.set_xlabel(x_label, fontsize=10, color='#a0a0a0')
    ax.set_ylabel(y_label, fontsize=10, color='#a0a0a0')
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.tick_params(colors='#a0a0a0')

    # Style the chart to match the dark theme
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#161b22')
    for spine in ax.spines.values():
        spine.set_edgecolor('#30363d')

    plt.tight_layout()
    output_path = CHARTS_DIR / filename
    plt.savefig(output_path, format='svg')
    plt.close(fig) # Close the figure to free up memory
    print(f"Successfully generated chart: {output_path}")


# --- Web Server Routes ---

@app.route("/")
def index():
    """Serves the main dashboard page."""
    return render_template("dashboard.html")

@app.route("/chart/<path:filename>")
def get_chart(filename):
    """Serves a specific chart image from the 'charts' directory."""
    return send_from_directory(CHARTS_DIR, filename, as_attachment=False)

@app.route("/generate/<sensor_type>")
def generate_chart_route(sensor_type):
    """
    API endpoint to trigger the generation of a specific sensor chart.
    This replaces the call to the shell script.
    """
    sensor_map = {
        "dht": lambda: generate_placeholder_chart("dht_chart.svg", "DHT Sensor Data", "Time", "Temp/Humidity", "#34a853"),
        "mpu": lambda: generate_placeholder_chart("mpu_chart.svg", "MPU-6050 IMU Data", "Time", "Rotation/Accel", "#4285f4"),
        "sound": lambda: generate_placeholder_chart("sound_chart.svg", "Sound Level Data", "Time", "Amplitude", "#fbbc05"),
    }

    if sensor_type not in sensor_map:
        return jsonify({"status": "error", "message": "Invalid sensor type specified."}), 400

    try:
        print(f"=== Generating {sensor_type.upper()} Chart ===")
        sensor_map[sensor_type]()
        # Add a small delay to ensure the file is written before the client requests it
        time.sleep(0.1)
        return jsonify({
            "status": "ok",
            "message": f"{sensor_type.upper()} chart generated successfully.",
            "chart_url": f"/chart/{sensor_type}_chart.svg"
        })
    except Exception as e:
        error_message = f"Failed to generate {sensor_type.upper()} chart: {e}"
        print(error_message, file=sys.stderr)
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == "__main__":
    # Note: Using host="0.0.0.0" makes the server accessible on your local network.
    app.run(host="0.0.0.0", port=5000, debug=True)

