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



~~~bash

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf

~~~

~~~bash

# --- Kabot-1 Hotspot DHCP Configuration ---
interface=wlan0        # Listen only on the Wi-Fi interface
dhcp-range=192.168.4.10,192.168.4.250,255.255.255.0,24h
                       # IP range for connected devices (from .10 to .250) for 24 hours
server=8.8.8.8         # Forward DNS requests (though devices won't access internet)
domain-suffix=kabot-1.local
                       # Optional: defines the local domain
address=/kabot-1.local/192.168.4.1
                       # Ensures that http://kabot-1.local always resolves to the Pi's IP



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



