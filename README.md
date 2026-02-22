
<div align="center">
  <!-- Hero Image / Memorial Banner – replace with actual photo of Kabot-1 or a symbolic image -->
  <img src="https://via.placeholder.com/1200x400/0A1929/FFFFFF?text=🕯️+In+Memoriam+-+Kabot-1+(ZR6BN)+🕯️" alt="memorial banner" width="100%">
  
  <h1>🕊️ Kabot-1 (ZR6BN) – The Little Payload That Touched the Sky</h1>
  
  <p><i>“She fell 30 km, but her memory (and her SD card) lived on.”</i></p>
  
  <!-- Memorial Badges -->
  <p>
    <img src="https://img.shields.io/badge/status-rest_in_peace-708090?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="Status: Rest in Peace">
    <img src="https://img.shields.io/badge/last_flight-11_October_2025-4682B4?style=for-the-badge&logo=airbnb&logoColor=white" alt="Last Flight">
    <img src="https://img.shields.io/badge/data-survived-success?style=for-the-badge&logo=icloud&logoColor=white" alt="Data Survived">
  </p>
  
  <!-- Quick navigation -->
  <h4>
    <a href="#-a-eulogy-for-kabot-1">📖 Eulogy</a> •
    <a href="#-what-she-taught-us">🔭 Lessons</a> •
    <a href="#-her-legacy-the-code">💻 Code</a> •
    <a href="#-project-tree">🌳 Tree</a> •
    <a href="#-installation--the-pip-fix">🛠️ Install</a> •
    <a href="#-usage">🚀 Usage</a> •
    <a href="#-future-kabot-2--beyond">✨ Future</a>
  </h4>
</div>

---

## 🕯️ A Eulogy for Kabot-1

> **FAZE OUT IN AFFECT NOTICE**  
> *As of Sunday 22 February 2026 @ 18:36 SAST*  

It is with heavy hearts and immense pride that we announce the **retirement of Kabot‑1 (ZR6BN)** – the benchmark payload that flew aboard BACAR13.  

On **11 October 2025**, she ascended into the blue, strapped to a helium balloon, destined for the edge of space. For hours she climbed, logging every gyro wobble, every CPU temperature spike, every whisper of wind. At **30 km altitude**, the balloon burst – as planned. But then, tragedy: **both main and emergency parachutes failed to deploy.**  

She fell.  

For long minutes, she tumbled toward Earth at terminal velocity. The ground rushed up. Impact. Silence.  

When we reached her wreckage, we expected a total loss. But there, among the twisted foam and broken electronics, her **flight computer – a humble Raspberry Pi Zero – was intact.** Its SD card, still clutching the data, was untouched.  

**Her body was broken, but her soul – her data – survived.**  

We brought her home. We pored over every line of code, every sensor reading, every heartbeat log. And we learned. Oh, how we learned.  

**Thank you, Kabot‑1. You gave everything for science. We salute you.** 🫡  

---

## 🔭 What She Taught Us

Kabot‑1 wasn't just a collection of sensors and scripts. She was our teacher.  

- **Performance matters** – her code ran on Raspberry OS Lite, and we learned its limits the hard way.  
- **Redundancy is not optional** – dual parachutes failed; next time we'll have triple.  
- **Data is sacred** – her SD card survived a 30 km impact. We now treat every byte as precious.  
- **Simplicity wins** – her most reliable subsystems were the simplest ones.  

Every line of code in this repository carries a lesson. Every chart is a memory.  

---

## 💻 Her Legacy: The Code

Though Kabot‑1 will never fly again, **her code lives on**. This archive contains the complete software stack that ran on her final flight:

- **Heartbeat loggers** for MPU6050, CPU temp, and sound levels – they ticked away until the very end.  
- **Plotting tools** that turned raw telemetry into beautiful SVGs – some of those charts are the last images she ever sent.  
- **Flight simulations** that helped us design her trajectory – and now help us plan her successors.  
- **A Wi‑Fi hotspot** that let us talk to her in the air – the last signal we received was "all systems nominal".  
- **A web dashboard** that displayed her vitals in real time – the screen went dark at 30 km.  

This isn't just code. It's a **digital memorial**.  

---

## 🌳 Project Tree

<details>
<summary>📁 Click to explore her remains – the full directory structure</summary>

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

🛠️ Installation & The Pip Fix (A Lesson from Kabot‑1)

Kabot‑1 ran on Raspberry Pi OS Lite (Bookworm 32‑bit). During development, we fought a silent enemy: the RAM disk. Pip kept failing with:

```
OSError: [Errno 28] No space left on device
```

It wasn't the SD card – it was /tmp filling up. We learned, we fixed, and we share that fix here in her honor.

🧰 The One‑Line Memorial Fix

Run this once from your project directory (where your virtual environment venv lives). It will create a permanent home for pip's temporary files – on the SD card, not in volatile RAM.

```bash
sudo mkdir -p /etc/profile.d /var/tmp/pip && sudo chmod 1777 /var/tmp/pip && echo 'export TMPDIR=/var/tmp/pip' | sudo tee /etc/profile.d/pip_tmpdir.sh > /dev/null && echo 'export TMPDIR=/var/tmp/pip' >> venv/bin/activate
```

What it does, and why Kabot‑1 would approve:

· Creates /var/tmp/pip – a place where temporary files can survive, just like her SD card survived.
· Makes it world‑writable – because sharing is caring.
· Sets TMPDIR globally and in your venv – ensuring every pip install uses this safe haven.

After that:

```bash
source venv/bin/activate
echo $TMPDIR   # should output /var/tmp/pip
pip install -r requirements.txt   # no more "No space left"
```

💡 Kabot‑1’s Tip: Add export TMPDIR=/var/tmp/pip to your ~/.bashrc so every future project remembers her lesson.

---

🚀 Using Her Code – A Manual

1️⃣ Start the Main Payload Script

```bash
python main.py
```

This launches the core logging – the same heartbeat that kept her alive until the end.

2️⃣ Access the Live Dashboard (If She Were Still Here)

Connect to her Wi‑Fi and open http://kabot1.local:5000. The last thing we saw was a green "NOMINAL" status.

3️⃣ Run Simulations – Relive Her Flight

```bash
python src/simulation/scripts/simulation_master.py
```

Simulate her ascent, her fall, and see what she experienced.

4️⃣ Generate Charts – Her Final Art

```bash
python src/plotter/cpu_plotter.py
python src/plotter/mpu6050_plotter.py
python src/plotter/sound_plotter.py
```

These SVGs are stored in src/plotter/charts/. They are her masterpieces.

---

✨ Future: Kabot‑2 & Beyond – Carrying Her Torch

Kabot‑1 may be gone, but her spirit ignites the future.

· Kabot‑2 – A bench‑test HAB payload running KabotFirmware, a custom OS built from the lessons she taught us.
· KabotSat Alpha – A cubesat, scheduled for 2028, that will carry her code into orbit.

We are building a website to share our journey – a place where her story will be told. Until then, explore her code, learn from her sacrifice, and keep reaching for the sky. ☁️

---

📄 License

This repository is dedicated to the public under the MIT License. Kabot‑1’s code is free for all to use, study, and improve – just as she would have wanted.

---

📬 Contact & Acknowledgements

Project Lead – Nathan Graham Busse

· Project Link: https://github.com/Nathan-Busse/kabot1

With deepest gratitude to:

· The BACAR13 launch team, who gave her a ride to the edge.
· Her flight computer, which kept ticking even through the fall.
· Her batteries, which held charge until the very last moment.
· Her ADC and SD card, which refused to let go of her memories.
· And to Kabot‑1 herself – you were more than hardware. You were family. 🫡

---

<div align="center">
  <img src="https://via.placeholder.com/1200x150/0A1929/FFFFFF?text=❤️+Forever+in+Our+Data+Logs+-+Kabot-1+❤️" alt="footer" width="100%">
  <br/>
  <sub>“Not all who wander are lost – some just fall 30 km and become legends.”</sub>
</div>
