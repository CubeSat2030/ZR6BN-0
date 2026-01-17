



IMPORTANT NOTE:
---------------
~~~

FAZE OUT IN AFFECT NOTICE:
​As of Saturday 17 January 2026 @ 12:54PM SAST the chart generation feaure is being fazed out entirely due to impracticallity towards:
​performance,
​effficiancly,
​reliability.
​However we decided to replace it with txt file retrieval instead. with that said the retrieval and downloading of txt files are still performed via Kabot-1's web_ui accessed locally on your web browser app.
​Later this year when Kabot-2's mission is green lit we will be fazing out the web_ui used in our kabot-1 HAB payload entirely. Kabot-2 however will use its client app, the KabotDockApp that is still in the drawing board phase.

~~~


# Project tree

~~~
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
~~~






# 🐍 Raspberry Pi OS Lite (Bookworm 32-bit) — Pip "No Space Left on Device" Fix

## 🧩 The Problem

When installing Python packages with `pip` on **Raspberry Pi OS Lite (Bookworm 32-bit)**, you might see an error like:

```
OSError: [Errno 28] No space left on device
```

Even though your SD card has plenty of free space.

### Why This Happens

By default, Raspberry Pi OS mounts `/tmp` as a **RAM disk (`tmpfs`)** — which is only a few hundred MB in size.  
`pip` uses `/tmp` to unpack and build packages before installing them, so large packages (like `numpy`, `pandas`, or `matplotlib`) can quickly fill it up.

---

## 🧰 The Fix

We'll redirect pip’s temporary build directory to a location on the SD card instead of RAM.

### ✅ One-line Command (Full Fix)

Run this **once** from your project directory (where your existing virtual environment `venv` lives):

```bash
sudo mkdir -p /etc/profile.d /var/tmp/pip && sudo chmod 1777 /var/tmp/pip && echo 'export TMPDIR=/var/tmp/pip' | sudo tee /etc/profile.d/pip_tmpdir.sh > /dev/null && echo 'export TMPDIR=/var/tmp/pip' >> venv/bin/activate
```

---

## 🧠 What This Does

1. **Creates** `/var/tmp/pip` on your SD card (not in RAM).  
2. **Makes it writable** for all users (`chmod 1777` — same permissions as `/tmp`).  
3. **Adds a global environment variable** so `TMPDIR=/var/tmp/pip` is used system-wide (including `sudo`).  
4. **Updates your existing `venv`** so it always uses `/var/tmp/pip` when activated.

---

## 🚀 Usage

After running the command:

```bash
source venv/bin/activate
echo $TMPDIR
```

You should see:
```
/var/tmp/pip
```

Now you can safely install large packages:

```bash
pip install numpy pandas matplotlib
```

No more “No space left on device” errors 🎉

---

## 🧩 Optional: Apply to All Future Virtual Environments

To automatically apply this fix to every new venv you create, add this line to your shell profile (`~/.bashrc` or `~/.profile`):

```bash
export TMPDIR=/var/tmp/pip
```

Then reload it:
```bash
source ~/.bashrc
```

---

## 🧼 Cleanup (if ever needed)

To undo this fix:

```bash
sudo rm -f /etc/profile.d/pip_tmpdir.sh
sudo rm -rf /var/tmp/pip
sed -i '/export TMPDIR=\/var\/tmp\/pip/d' venv/bin/activate
```

---

### 🧾 Summary

| Component | Old Location | New Safe Location |
|------------|---------------|------------------|
| Pip temporary builds | `/tmp` (RAM, small) | `/var/tmp/pip` (SD card, large) |

✅ Fix is **persistent**, **system-wide**, and **venv-safe**.







