~~~
create a 3D fly-through simulation based on motion data, stored in the .txt file called MPU6050.


Here is the file structure:


kabot-1(our root folder)

 |

 |

 |-->   src--> logger--> data-|

           |                                        |_MPU6050.txt

           |

           |--> simulation--> scripts--> simulation.cpp 

                                                      |-->  simulation_pipeline_scripts--> cube.cpp

                                                                                                               |--> physics.cpp

                                                                                                               |--> graphics.cpp

                                                                                                                |--> render.cpp




~~~


# Project tree

~~~

├── .gitattributes
├── README.md
├── main.py
├── mission_master.log
├── requirements.txt
├── simulation_gouverner.log
├── src/
│   ├── .gitkeeep
│   ├── logger/
│   │   ├── __pycache__/
│   │   │   └── heartbeat.cpython-313.pyc
│   │   ├── calibrate_sound.py
│   │   ├── cpu_logger.py
│   │   ├── data/
│   │   │   ├── CPU_TEMP.txt
│   │   │   ├── LATEST_SENSOR_DATA.json
│   │   │   ├── LATEST_SYSTEM_STATUS.json
│   │   │   ├── MPU6050.txt
│   │   │   ├── sound_data_D0.txt
│   │   │   └── sound_data_D0_backup.txt
│   │   ├── heartbeat.py
│   │   ├── heartbeats/
│   │   │   ├── cpu_logger.json
│   │   │   └── mpu_logger.json
│   │   ├── mpu6050_logger.py
│   │   └── sound_logger.py
│   ├── media/
│   │   ├── .gitkeep
│   │   └── output/
│   │       ├── .gitkeep
│   │       ├── image/
│   │       │   └── .gitkeep
│   │       └── video/
│   │           └── .gitkeep
│   ├── plotter/
│   │   ├── charts/
│   │   │   ├── cpu_chart.svg
│   │   │   ├── cpu_chart_backup.svg
│   │   │   ├── mpu_chart.svg
│   │   │   ├── mpu_chart_backup.svg
│   │   │   └── mpu_phases.svg
│   │   ├── cpu_plotter.py
│   │   ├── mpu6050_plotter.py
│   │   └── sound_plotter.py
│   └── simulation/
│       ├── .gitkeep
│       └── scripts/
│           ├── simulation_gouverner.py
│           └── simulation_pipeline/
│               ├── preprocess.py
│               ├── render.py
│               ├── sensor_fusion.py
│               └── trajectory.py
└── web_ui/
    ├── app_server.py
    └── templates/
        └── dashboard.html
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







