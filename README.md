~~~bash


Sudo apt update
sudo apt install hostapd dnsmasq -y
sudo apt install avahi-daemon -y # For .local address support


~~~


**File structure:**


~~~bash

sudo nano /etc/dhcpcd.conf

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



