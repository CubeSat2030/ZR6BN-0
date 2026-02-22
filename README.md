<div align="center">
  <!-- Header Image – replace with your own photo of Kabot-1 or a cool graphic -->
  <img src="https://via.placeholder.com/1200x300/0A1929/FFFFFF?text=🎈+Kabot-1+Payload+Archive+🎈" alt="header" width="100%">
  
  <h1>🚀 Kabot-1 (ZR6BN) – Flight Archive</h1>
  
  <p><i>“She fell 30 km, but her data survived. This repository is a tribute to everything we learned.”</i></p>
  
  <!-- Status badges – note the “discontinued” badge with a salute -->
  <p>
    <img src="https://img.shields.io/badge/status-discontinued-important?style=for-the-badge&logo=raspberrypi&color=red" alt="Status: Discontinued">
    <img src="https://img.shields.io/badge/last_flight-11_October_2025-9cf?style=for-the-badge&logo=airbnb&logoColor=white" alt="Last Flight">
  </p>
  
  <!-- Quick navigation -->
  <h4>
    <a href="#-tribute--the-story-of-kabot-1">📖 Tribute</a> •
    <a href="#-project-overview">🔭 Overview</a> •
    <a href="#-project-tree">🌳 Tree</a> •
    <a href="#-installation--the-pip-fix">🛠️ Install</a> •
    <a href="#-usage">🚀 Usage</a> •
    <a href="#-future-kabot-2--beyond">✨ Future</a>
  </h4>
</div>

---

## 📖 Tribute & The Story of Kabot‑1

> **FAZE OUT IN AFFECT NOTICE**  
> *As of Sunday 22 February 2026 @ 18:36 SAST*  

The development of **Kabot‑1 (ZR6BN)** – the benchmark payload that flew on board BACAR13 – is being discontinued entirely due to impracticality in performance, efficiency, and reliability.  

**However**, we learned an enormous amount from building her and from studying her remains after she hit the ground **30 km up** when both main and emergency parachutes failed to deploy upon burst.  

Despite being mangled, her **flight computer was intact** – all data survived. We poked around her code extensively to see what could be improved.  

**Thank you, Kabot‑1. We salute you.** 🫡  

Later this year, when Kabot‑2’s mission is green‑lit, we will be phasing out Raspberry OS Lite in favour of a custom OS called **KabotFirmware**. KabotFirmware will be the heart of the Kabot‑2 bench‑test HAB payload, future payloads, and the **KabotSat Alpha cubesat** (scheduled for completion by 2028 at the earliest).  

Unfortunately, this means that **Kabot‑1 will be the only repository that is made public**. However, we are working on a website to share our development journey.

---

## 🔭 Project Overview

Kabot‑1 was a high‑altitude balloon payload designed to log sensor data (MPU6050, CPU temperature, sound), provide a Wi‑Fi hotspot for in‑flight access, simulate trajectories, and generate post‑flight visualisations.  

Even though the hardware is gone, the software lives on. This archive contains everything we used – from logging scripts to the web dashboard.

### ✨ Key Components

| Component | Description |
|-----------|-------------|
| **Logger** | Heartbeat‑style logging of MPU6050, CPU temp, and sound levels (pre‑flight, in‑flight, post‑flight) |
| **Plotter** | Generates SVG charts from logged data (CPU, MPU, sound, phases) |
| **Simulation** | Full‑flight simulator with sensor fusion, trajectory rendering, and preprocessing |
| **Hotspot** | Turns the Raspberry Pi into an access point for in‑flight connectivity (hostapd + dnsmasq) |
| **Web UI** | Flask‑based dashboard to monitor the payload live |
| **Presentation** | Special mode for displaying data in a clean, slideshow‑like format |

---

## 🌳 Project Tree

<details>
<summary>📁 Click to expand the full directory structure</summary>

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

🛠️ Installation & The “Pip No Space” Fix

Because Kabot‑1 ran on Raspberry Pi OS Lite (Bookworm 32‑bit), you may encounter a classic issue when installing large Python packages with pip.

🧩 The Problem

```
OSError: [Errno 28] No space left on device
```

Even if your SD card has plenty of free space, /tmp is mounted as RAM (tmpfs) and is only a few hundred MB. Pip unpacks packages there, so big libraries like numpy, pandas, or matplotlib can fill it up.

🧰 The One‑Line Fix

Run this once from your project directory (where your virtual environment venv lives):

```bash
sudo mkdir -p /etc/profile.d /var/tmp/pip && sudo chmod 1777 /var/tmp/pip && echo 'export TMPDIR=/var/tmp/pip' | sudo tee /etc/profile.d/pip_tmpdir.sh > /dev/null && echo 'export TMPDIR=/var/tmp/pip' >> venv/bin/activate
```

What it does:

· Creates /var/tmp/pip on the SD card (not in RAM) and makes it world‑writable.
· Sets the TMPDIR environment variable globally and inside your venv, so pip always uses the new location.

After that, activate your environment and verify:

```bash
source venv/bin/activate
echo $TMPDIR   # should output /var/tmp/pip
pip install -r requirements.txt   # now works smoothly
```

💡 Optional: Add export TMPDIR=/var/tmp/pip to your ~/.bashrc to apply it to all future virtual environments.

---

🚀 Usage

1️⃣ Start the Main Payload Script

```bash
python main.py
```

This will launch the core logging and, depending on configuration, the Wi‑Fi hotspot and web dashboard.

2️⃣ Access the Live Dashboard

If the hotspot is active, connect to the Kabot‑1 Wi‑Fi and open http://kabot1.local:5000 (or the IP assigned).

3️⃣ Run Simulations Offline

```bash
python src/simulation/scripts/simulation_master.py
```

Simulation outputs can be found in src/simulation/output/.

4️⃣ Generate Charts from Logged Data

```bash
python src/plotter/cpu_plotter.py
python src/plotter/mpu6050_plotter.py
python src/plotter/sound_plotter.py
```

Charts are saved as SVGs in src/plotter/charts/.

---

✨ Future: Kabot‑2 & Beyond

While Kabot‑1 rests, her spirit flies on in Kabot‑2 and eventually KabotSat Alpha.

· ✅ Kabot‑2 – Bench‑test HAB payload with custom firmware called KabotFirmware.
· 🛰️ KabotSat Alpha – A cubesat scheduled to complete its construction by 2028, running the same firmware core.

We’ll be sharing our journey on a dedicated website (coming soon). Until then, explore the code, learn from our mistakes, and keep reaching for the sky. ☁️

---

📄 License

Distributed under the MIT License. See LICENSE for more information.

---

📬 Contact & Acknowledgements

Project Lead – Your Name

· 📧 email@example.com
· 🐦 @twitter_handle

Project Link: https://github.com/yourname/kabot1

Special thanks to everyone who supported the BACAR13 launch and to the data that survived a 30 km fall. 🫡

---

<div align="center">
  <img src="https://via.placeholder.com/1200x100/0A1929/FFFFFF?text=❤️+Salute+Kabot-1+❤️" alt="footer" 
