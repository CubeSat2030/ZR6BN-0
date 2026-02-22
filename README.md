
<div align="center">
  <!-- Hero Image / Mission Patch – replace with actual photo of Kabot-1 or a symbolic mission patch -->
  <img src="https://via.placeholder.com/1200x400/0A1929/FFFFFF?text=🛰️+Kabot-1+(ZR6BN)+-+Mission+Complete+🛰️" alt="mission banner" width="100%">
  
  <h1>🛸 Kabot-1 (ZR6BN) – Mission Archive</h1>
  
  <p><i>“She fell 30 km, but her memory and her data endure. This repository preserves the software, the lessons, and the legacy of a pioneering payload.”</i></p>
  
  <!-- Mission Status Badges -->
  <p>
    <img src="https://img.shields.io/badge/status-mission_completed-708090?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="Status: Mission Completed">
    <img src="https://img.shields.io/badge/last_flight-11_October_2025-4682B4?style=for-the-badge&logo=airbnb&logoColor=white" alt="Last Flight">
    <img src="https://img.shields.io/badge/data_survival-100%25-success?style=for-the-badge&logo=icloud&logoColor=white" alt="Data Survival: 100%">
    <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge&logo=open-source-initiative" alt="License: MIT">
  </p>
  
  <!-- Quick navigation -->
  <h4>
    <a href="#-mission-summary">📋 Summary</a> •
    <a href="#-science-and-engineering-highlights">🔭 Highlights</a> •
    <a href="#-data-legacy">📊 Data</a> •
    <a href="#-project-tree">🌳 Tree</a> •
    <a href="#-installation--the-pip-fix">🛠️ Install</a> •
    <a href="#-usage">🚀 Usage</a> •
    <a href="#-future-missions">✨ Future</a>
  </h4>
</div>

---

## 📋 Mission Summary

**Kabot‑1 (callsign ZR6BN)** was a technology demonstration and scientific payload developed by [Your Team/Org] and launched aboard the BACAR13 high‑altitude balloon on **11 October 2025**. Its primary objectives were:

- Validate a low‑cost, Raspberry‑Pi‑based flight computer for near‑space environments.
- Collect synchronized sensor data (IMU, CPU temperature, acoustic levels) throughout ascent, float, and descent.
- Demonstrate autonomous Wi‑Fi hotspot functionality for in‑flight telemetry.
- Develop a reusable software framework for future high‑altitude and orbital missions.

After a successful ascent to **30 km**, the balloon burst as expected. However, due to a dual‑parachute failure, the payload experienced an unplanned high‑velocity impact. Despite extensive physical damage, the **flight computer and its SD card remained intact**, resulting in **100% data recovery**.

Based on post‑flight analysis and lessons learned, the team has decided to **conclude Kabot‑1 operations** and focus resources on its successors: **Kabot‑2** and **KabotSat Alpha**. This repository serves as the complete software archive for Kabot‑1, preserving its code, data, and engineering legacy for the open‑source community.

---

## 🔭 Science and Engineering Highlights

| Achievement | Description |
|-------------|-------------|
| **Full Data Return** | All sensor logs from pre‑flight, ascent, float, and descent were recovered, providing a complete profile of the flight. |
| **Flight Computer Survivability** | The Raspberry Pi Zero continued logging until impact; the SD card withstood 30 km fall and remained readable. |
| **Wi‑Fi Hotspot** | Successfully demonstrated autonomous access‑point mode, allowing real‑time monitoring up to the burst altitude. |
| **Sensor Fusion** | IMU and temperature data were correlated with flight dynamics, offering insights into the vehicle’s behavior during ascent and tumbling descent. |
| **Software Modularity** | The logging, plotting, simulation, and dashboard components are reusable and have been adapted for Kabot‑2 planning. |

> *“Kabot‑1 exceeded its design life by continuing to log data until the moment of impact. Its robust construction and thoughtful software design turned a hard landing into a complete data return.”* – Mission Manager

---

## 📊 Data Legacy

The data recovered from Kabot‑1’s SD card is archived in this repository under `src/logger/data/`. It includes:

- **MPU6050 inertial measurements** (acceleration, gyroscope) throughout the flight.
- **CPU temperature** of the flight computer, showing thermal trends in near‑space.
- **Acoustic levels** from the sound sensor, calibrated and logged.
- **Backup copies** automatically created during flight for redundancy.

All data is provided in plain text format (`.txt`, `.json`) and can be visualized using the included plotting tools.

---

## 🌳 Project Tree

<details>
<summary>📁 Click to expand the full software archive structure</summary>

```bash
├── .gitattributes
├── README.md
├── SystemClone/
│   ├── .gitkeep
│   ├── RunSystemClone.py
│   └── src/
│       └── clone.py
├── kabot_launchpad/
│   ├── configs/
│   │   ├── dnsmasq.conf
│   │   └── hostapd.conf
│   ├── logs/
│   │   ├── ap_startup.log
│   │   └── dhcp_leases.log
│   ├── scripts/
│   │   ├── dnsmasq.conf
│   │   ├── install_hotspot_deps.sh
│   │   ├── kabot1_hotspot.py
│   │   └── kabot1_stop_ap.py
│   └── tests/
│       └── connecivity_check.py
├── main.py
├── requirements.txt
├── src/
│   ├── .gitkeeep
│   ├── logger/
│   │   ├── __pycache__/
│   │   │   └── heartbeat.cpython-313.pyc
│   │   ├── data/
│   │   │   ├── .gitkeep
│   │   │   ├── 1_preflight/
│   │   │   │   └── sound_logger_config.txt
│   │   │   ├── 2_inflight/
│   │   │   │   ├── .gitkeep
│   │   │   │   ├── MPU6050.txt
│   │   │   │   ├── backup/
│   │   │   │   │   ├── .gitkeep
│   │   │   │   │   ├── inflight_MPU6050_backup.txt
│   │   │   │   │   └── inflight_cpu_temp_backup.txt
│   │   │   │   └── cpu_temp.txt
│   │   │   └── 3_postflight/
│   │   │       ├── .gitkeep
│   │   │       └── sound_logger.txt
│   │   ├── heartbeats/
│   │   │   ├── cpu_logger.json
│   │   │   ├── mpu_logger.json
│   │   │   └── sound_logger.json
│   │   └── scripts/
│   │       ├── calibrate_sound.py
│   │       ├── cpu_temp_logger.py
│   │       ├── heartbeat.py
│   │       ├── mpu6050_logger.py
│   │       └── sound_logger.py
│   ├── plotter/
│   │   ├── charts/
│   │   │   ├── cpu_chart.svg
│   │   │   ├── cpu_chart_backup.svg
│   │   │   ├── mpu_chart.svg
│   │   │   ├── mpu_chart_backup.svg
│   │   │   ├── mpu_phases.svg
│   │   │   └── sound_chart.svg
│   │   ├── cpu_plotter.py
│   │   ├── mpu6050_plotter.py
│   │   └── sound_plotter.py
│   ├── presentation/
│   │   ├── activate_presentation_mode.py
│   │   ├── presentation_handler.py
│   │   └── presentation_runtime.py
│   ├── simulation/
│   │   ├── .gitkeep
│   │   ├── output/
│   │   │   └── data/
│   │   │       └── preprocessed.csv
│   │   └── scripts/
│   │       ├── payload_flight_simulation.py
│   │       ├── simulation.py
│   │       ├── simulation_master.log
│   │       ├── simulation_master.py
│   │       └── simulation_pipeline/
│   │           ├── preprocess.py
│   │           ├── render_vectors.py
│   │           ├── sensor_fusion.py
│   │           └── trajectory.py
│   └── tools/
│       └── dataplot.py
└── web_ui/
    ├── app_server.py
    ├── app_server_development.py
    ├── app_server_rollback.py
    └── templates/
        ├── dashboard.html
        ├── dashboard_development.html
        └── dashboard_rollback.html
```

</details>

---

🛠️ Installation & The Pip Fix (Lessons Learned)

During development, the team encountered a known limitation of Raspberry Pi OS Lite: pip uses /tmp (a RAM disk) for building packages, which can fill up quickly when installing large libraries like numpy or pandas. This issue was diagnosed and mitigated, and the solution is documented here for future missions.

🧩 The Problem

```
OSError: [Errno 28] No space left on device
```

Even with ample free space on the SD card, /tmp is a small tmpfs filesystem. Pip’s build process exhausts it.

🧰 The Fix

Run this once from your project directory (where your virtual environment venv lives):

```bash
sudo mkdir -p /etc/profile.d /var/tmp/pip && sudo chmod 1777 /var/tmp/pip && echo 'export TMPDIR=/var/tmp/pip' | sudo tee /etc/profile.d/pip_tmpdir.sh > /dev/null && echo 'export TMPDIR=/var/tmp/pip' >> venv/bin/activate
```

What it accomplishes:

· Creates /var/tmp/pip on the SD card (persistent storage) with world‑writable permissions.
· Sets the TMPDIR environment variable system‑wide and inside the active virtual environment, redirecting pip’s temporary files to the SD card.

After applying, verify:

```bash
source venv/bin/activate
echo $TMPDIR   # should output /var/tmp/pip
pip install -r requirements.txt   # now completes successfully
```

💡 For future missions: Add export TMPDIR=/var/tmp/pip to your ~/.bashrc to apply this fix to all new virtual environments.

---

🚀 Using the Kabot‑1 Software Suite

1️⃣ Launch the Main Payload Simulator / Logger

```bash
python main.py
```

This will initialize logging modules and, if configured, the Wi‑Fi hotspot and web dashboard.

2️⃣ Access the Live Dashboard (Simulated or Real-Time)

If the hotspot is active, connect to kabot1 Wi‑Fi and navigate to http://kabot1.local:5000.

3️⃣ Replay the Flight with Simulation Tools

```bash
python src/simulation/scripts/simulation_master.py
```

Simulation outputs are saved in src/simulation/output/.

4️⃣ Generate Post‑Flight Plots

```bash
python src/plotter/cpu_plotter.py
python src/plotter/mpu6050_plotter.py
python src/plotter/sound_plotter.py
```

Plots are stored as SVGs in src/plotter/charts/.

---

✨ Future Missions: Kabot‑2 and KabotSat Alpha

Kabot‑1’s successful data return and the engineering insights gained have directly informed the design of its successors:

· Kabot‑2 – A bench‑test and high‑altitude balloon payload featuring KabotFirmware, a custom real‑time operating system derived from Kabot‑1’s software stack. Scheduled for launch in late 2026.
· KabotSat Alpha – A 1U CubeSat mission, targeted for completion by 2028, that will carry Kabot‑derived sensor and communication systems into low Earth orbit.

This repository will remain public as a reference and a foundation for these upcoming missions. A dedicated project website is in development to share progress and open‑source contributions.

---

📄 License

The software and documentation in this repository are released under the MIT License. We encourage you to use, modify, and build upon Kabot‑1’s legacy in your own projects.

---

📬 Contact and Credits

Mission Lead – Nathan Graham Busse

· GitHub: Nathan-Busse
· Project Repository: https://github.com/Nathan-Busse/kabot1

Acknowledgments

· The BACAR13 launch team for providing the flight opportunity.
· The resilient hardware: Raspberry Pi Zero, MPU6050, ADC, and the SanDisk Ultra SD card that survived a 30 km fall.
· Everyone who supported the mission with advice, encouragement, and ground support.

---

<div align="center">
  <img src="https://via.placeholder.com/1200x150/0A1929/FFFFFF?text=🛰️+Kabot-1+Mission+Archive+-+Data+Forever+🛰️" alt="footer" width="100%">
  <br/>
  <sub>“Every mission ends, but the data – and the knowledge – live on.”</sub>
</div>
