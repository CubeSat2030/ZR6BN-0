~~~bash


Sudo apt update
sudo apt install hostapd dnsmasq -y
sudo apt install avahi-daemon -y # For .local address support


~~~





~~~bash

sudo nano /etc/dhcpcd.conf

~~~

~~~bash

# --- Static IP configuration for Kabot-1 Hotspot (wlan0) ---
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant



~~~


**File structure:**
~~~

├── .gitattributes
├── README.md
├── main.py
├── src/
│   ├── logger/
│   │   ├── dht_logger.py
│   │   ├── mpu6050_logger.py
│   │   └── sound_logger.py
│   └── plotter/
│       ├── dht_plotter.py
│       ├── mpu6050_plotter.py
│       └── sound_plotter.py
└── web_ui/
    ├── app_server.py
    └── templates/
        └── dashboard.html


~~~



