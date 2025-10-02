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
