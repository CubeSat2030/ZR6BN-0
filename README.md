~~~ bash
sudo apt update
~~~

~~~ bash
sudo apt upgrade -y
~~~

~~~ bash
sudo reboot
~~~

~~~ bash
sudo raspi-config
~~~

Perfect 👍 — here’s the expanded INSTALLATION.md including the Bluetooth PAN (Personal Area Network) setup on Raspberry Pi OS Lite (headless).

You can drop this straight into your repo:

⸻

🚀 Kabot-1 Mission Control – Installation & Setup Guide

This guide covers installing all dependencies and setting up the Mission Control Dashboard on a Raspberry Pi Zero W v1.2 running Raspberry Pi OS Lite.

The dashboard runs only over Bluetooth PAN at http://192.168.50.1:5000/, while Wi-Fi remains available for telemetry or uplink.

⸻

1️⃣ System Preparation

Update and install core tools:

sudo apt update && sudo apt upgrade -y
sudo apt install -y git git-lfs python3 python3-venv python3-pip bluez bluez-tools


⸻

2️⃣ Git & Repository Setup

Enable Git LFS:

git lfs install

Clone your repo (replace <YOUR_REPO_URL>):

git clone <YOUR_REPO_URL> kabot1
cd kabot1


⸻

3️⃣ Python Virtual Environment

Create and activate a venv:

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel

Install dependencies (from requirements.txt):

pip install -r requirements.txt

Example requirements.txt might contain:

flask
gpiozero
RPi.GPIO
numpy
matplotlib
pyserial


⸻

4️⃣ File Structure Verification

After cloning, you should see:

├── main.py
├── src/
│   ├── logger/
│   │   ├── data/
│   └── tracking/
└── web_ui/
    ├── app_server.py
    └── templates/


⸻

5️⃣ Configure Bluetooth PAN (Personal Area Network)
	1.	Enable Bluetooth daemon (already enabled by default on Pi OS Lite):

sudo systemctl enable bluetooth
sudo systemctl start bluetooth

	2.	Set up a PAN network:

Install bridge-utils (if not already present):

sudo apt install -y bridge-utils

	3.	Assign a static IP for PAN:

Create a PAN interface config at:

sudo nano /etc/network/interfaces.d/bnep0

Add:

auto bnep0
iface bnep0 inet static
    address 192.168.50.1
    netmask 255.255.255.0

	4.	Enable PAN role (NAP – Network Access Point):

Run in bluetoothctl:

bluetoothctl
power on
agent on
default-agent
discoverable on
pairable on

Then trust and pair your ground station device.

Finally, run:

sudo bt-network -s nap bnep0

This attaches the PAN to bnep0.

Your Pi is now hosting a small Bluetooth network at 192.168.50.1.

⸻

6️⃣ Running the Dashboard

Start manually:

cd ~/kabot1/web_ui
source ../venv/bin/activate
python3 app_server.py

On your ground station device, pair with the Pi, connect to the PAN, then open:

http://192.168.50.1:5000/


⸻

7️⃣ Data & Logs
	•	Logs and sensor data:

src/logger/data/


	•	Charts:

src/plotter/



Use the web UI to wipe or regenerate before each flight.

⸻

8️⃣ Optional: Autostart on Boot

Create a systemd service if you want auto-start (optional):

sudo nano /etc/systemd/system/webui.service

[Unit]
Description=Kabot-1 Mission Control Dashboard
After=network.target bluetooth.target

[Service]
ExecStart=/home/pi/kabot1/venv/bin/python /home/pi/kabot1/web_ui/app_server.py
WorkingDirectory=/home/pi/kabot1/web_ui
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

Enable:

sudo systemctl enable webui
sudo systemctl start webui


⸻

✅ At this stage you have:
	•	Git & Git LFS installed
	•	Python venv set up
	•	Flask web UI bound to 192.168.50.1
	•	Bluetooth PAN configured
	•	Data logging & wipe functions operational

⸻

Would you like me to also add a diagram of the network architecture (Pi ↔ Bluetooth PAN ↔ Ground Station) into the Markdown file so it’s visual and easier for new contributors?




~~~

├── .gitattributes
├── README.md
├── main.py
├── src/
│   ├── .gitkeeep
│   ├── downlink/
│   │   ├── .gitkeeep
│   │   ├── downlink.py
│   │   ├── event_listeners/
│   │   │   ├── bmp280_event_listener.py
│   │   │   ├── mpu6050_event_listener.py
│   │   │   └── sim7600E_event_listener.py
│   │   └── event_triggers/
│   │       ├── bmp280_event_trigger.py
│   │       ├── mpu6050_event_trigger.py
│   │       └── sim7600E_event_trigger.py
│   ├── logger/
│   │   ├── bmp280_logger.py
│   │   ├── data/
│   │   │   ├── DHT11.txt
│   │   │   ├── LATEST_SENSOR_DATA.json
│   │   │   ├── MPU6050.txt
│   │   │   ├── sound_data_D0.txt
│   │   │   └── sound_data_D0_backup.txt
│   │   ├── dht_logger.py
│   │   ├── mpu6050_logger.py
│   │   └── sound_logger.py
│   ├── photography/
│   │   ├── footage/
│   │   │   ├── .gitkeep
│   │   │   ├── images/
│   │   │   │   └── .gitkeep
│   │   │   └── videos/
│   │   │       └── .gitkeep
│   │   ├── image_capture.py
│   │   └── video_capture.py
│   ├── plotter/
│   │   ├── bmp280_plotter.py
│   │   ├── dht_plotter.py
│   │   ├── mpu6050_plotter.py
│   │   └── sound_plotter.py
│   └── tracking/
│       └── gps.py
└── web_ui/
    ├── app_server.py
    └── templates/
        └── dashboard.html
~~~
