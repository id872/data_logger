# data_logger
Writing device data to CSV file. Sending encrypted JSON request to insert the data into remote DB.

# What is it and what is for?

It is an application for logging data from various type of devices. Device’s readout can be logged into CSV file and/or remote database by encrypted JSON request. It will be described further below. See also the [web app](https://github.com/id872/devmon) (which is a second part of the project) - it is used for inserting devices data into DB and data presentation.

The application logs data from the following devices:
* Santerno Solar Inverters via Modbus protocol (https://en.wikipedia.org/wiki/Solar_inverter)
* DS18B20 temperature sensors via 1-Wire protocol (https://www.maximintegrated.com/en/products/sensors/DS18B20.html)
* Xiaomi Air Purifier 2H via WiFi (https://www.mi.com/global/mi-air-purifier-2h)
* Tasmota Plugs via WiFi(https://tasmota.github.io/docs/Tuya-Convert/)

This is personal project. It has been implemented mainly for tracking a performance of my solar installation. Another devices were added in a further development. This application runs on Raspberry Pi Zero with Python 3.6+

Feel free to fork and improve according to your needs.

# Summary, features, general info

There are five root packages in the project:

1. Configuration package contains a configurations for devices (grouped by protocol and device type). This package contains also CSV logging settings and JSON request settings (authentication data and the server URL).
2. Device package contains an implementation for handling devices. Each device is configured in the „Configuration” package.
3. Loggers package. Here are loggers for devices defined. Each device type (ex. Santerno Solar  Inverter, DS18B20 sensor etc.) has own data logger.
4. Logdata contains implementation for CSV files writing and encrypted JSON request (preparing encrypted device data for server). See the second project for handling JSON data: https://github.com/id872/devmon
5. Request contains implementation for POST request for encrypted JSON data. Device data compression and encryption is implemented in the aes_helper.py

Adding devices that are already implemented is easy – configuration update only.
To handle new device for logging, following items need to be created:

* (**2**) device implementation
* (**1**) device configuration
* (**3**) device logger
* and new JsonRequestType for new device (data_config.py)

The application is quite flexible. It logs devices data to proper, defined locations in the configuration package (**1**). JSON data manager checks server response and clears devices readouts if it was inserted into DB.

Like mentioned before, devices data can be logged into CSV files.
CSV files are created every new day. If there is no “today’s” file, a new file is created. If the file already exists, device readout is appended only (if there is a power cut for a while, Raspberry Pi will boot up and continue to write existing files). There is one CSV file for a group of devices. So one file per day for DS18B20 sensors, Santerno inverters etc. See the listing section to see CSV content examples.

# Compressed, encrypted JSON request mechanism 
It is used for inserting devices readouts into a remote database. JSON request contains following keys:
* data – encrypted JSON data containing username, password and devices readouts
* hash – API hash for particular user (encoded in base64)

JSON request data is encrypted by *api_key* from auth_conf.json file in the configs.json package.
The same *api_key* for particular user need to be present in the remote database to allow a web application to decrypt devices data.

There are following actions performed to send devices data to a database on a server.
1. json_data_manager.py prepares JSON request data with devices readouts
2. aes_helper.py compresses the JSON data to zlib format and encrypts compressed data. Output is base64 string.
3. post_request.py sends encrypted data (base64 string) to the server via POST request.

# Application run
It can be run with screen:
```shell
screen -d -m python3 /root/data_logger/device_data_logger.py
```

Reattach:
```shell
screen -r
```

Detach:
```shell
CTRL+a d
```

# Application log and CSV file content examples
Here are application log and CSV files content presented.
Note: application log file is created in the <app_root_dir>/.logs folder.

## Below is application log. Log level can be set in the device_data_logger.py
```
21-12-20_15:23:46.782, [ds18b20_logger.py/__initialize_sensors] -- DEBUG --> Initializing [Room] sensor
21-12-20_15:23:46.792, [w1_ds18b20.py/try_initialize] -- DEBUG --> Sensor '02162cffffff' ('Room') initialized
21-12-20_15:23:46.797, [ds18b20_logger.py/__init__] -- INFO --> Measuring temperature...
21-12-20_15:23:46.800, [airpurifier_logger.py/__initialize_device] -- DEBUG --> Initializing AirPurifier device
21-12-20_15:23:46.806, [wifi_airpurifier.py/try_initialize] -- DEBUG --> AirPurifier device [192.168.0.77] initialized
21-12-20_15:23:46.808, [airpurifier_logger.py/__init__] -- INFO --> Airpurifier data logging...
21-12-20_15:23:46.812, [tasmota_plug_logger.py/__initialize_device] -- DEBUG --> Initializing AirPurifier device
21-12-20_15:23:46.830, [tasmota_plug_logger.py/__init__] -- INFO --> Tasmota data logging...
21-12-20_15:23:47.337, [tasmota_plug_logger.py/__write_data] -- DEBUG --> LanbergPlug [192.168.0.99] -> data read time: 0.52 ms. Read error counter: 0
21-12-20_15:23:47.673, [tasmota_plug_logger.py/__write_data] -- DEBUG --> BlitzwolfPlug [192.168.0.123] -> data read time: 0.33 ms. Read error counter: 0
21-12-20_15:23:47.731, [csv_data_manager.py/get_file_to_write] -- DEBUG --> New file need to be created...
21-12-20_15:23:47.751, [device_data_csv_writer.py/__write_data_to_file] -- DEBUG --> Written device data:
{'Date_Time': '21-12-20_15:23:46', 'LanbergPlug_ac_power': 27, 'LanbergPlug_ac_voltage': 212, 'LanbergPlug_ac_current': 0.217, 'BlitzwolfPlug_ac_power': 48, 'BlitzwolfPlug_ac_voltage': 212, 'BlitzwolfPlug_ac_current': 0.345} to:
/home/logs/Tasmota/Tasmota_2020-12-21_15:23:47.csv
21-12-20_15:23:48.525, [airpurifier_logger.py/__write_data] -- DEBUG --> XiaomiAirPurifier2 [192.168.0.77] -> data read time: 1.72 ms. Read error counter: 0
21-12-20_15:23:48.578, [csv_data_manager.py/get_file_to_write] -- DEBUG --> New file need to be created...
21-12-20_15:23:48.583, [device_data_csv_writer.py/__write_data_to_file] -- DEBUG --> Written device data:
{'Date_Time': '21-12-20_15:23:46', 'XiaomiAirPurifier2_aqi': 32, 'XiaomiAirPurifier2_humidity': 49, 'XiaomiAirPurifier2_temperature': 22.1, 'XiaomiAirPurifier2_fan_rpm': 700} to:
/home/logs/Purifier/Purifier_2020-12-21_15:23:48.csv
21-12-20_15:25:01.862, [ds18b20_logger.py/__write_temperatures] -- DEBUG --> Room [02162cffffff] -> data read time: 5.30 ms. Read error counter: 0
21-12-20_15:25:01.914, [csv_data_manager.py/get_file_to_write] -- DEBUG --> New file need to be created...
21-12-20_15:25:01.919, [device_data_csv_writer.py/__write_data_to_file] -- DEBUG --> Written device data:
{'Date_Time': '21-12-20_15:25:01', 'Room_temperature': '24.5'} to:
/home/logs/Temperature/Temperature_2020-12-21_15:25:01.csv
21-12-20_15:27:48.111, [tasmota_plug_logger.py/__write_data] -- DEBUG --> LanbergPlug [192.168.0.99] -> data read time: 0.24 ms. Read error counter: 0
21-12-20_15:27:48.241, [tasmota_plug_logger.py/__write_data] -- DEBUG --> BlitzwolfPlug [192.168.0.123] -> data read time: 0.13 ms. Read error counter: 0
21-12-20_15:27:48.267, [device_data_csv_writer.py/__write_data_to_file] -- DEBUG --> Written device data:
{'Date_Time': '21-12-20_15:27:47', 'LanbergPlug_ac_power': 27, 'LanbergPlug_ac_voltage': 212, 'LanbergPlug_ac_current': 0.215, 'BlitzwolfPlug_ac_power': 46, 'BlitzwolfPlug_ac_voltage': 212, 'BlitzwolfPlug_ac_current': 0.341} to:
/home/logs/Tasmota/Tasmota_2020-12-21_15:23:47.csv
21-12-20_15:28:54.222, [airpurifier_logger.py/__write_data] -- DEBUG --> XiaomiAirPurifier2 [192.168.0.77] -> data read time: 5.49 ms. Read error counter: 0
21-12-20_15:28:54.281, [device_data_csv_writer.py/__write_data_to_file] -- DEBUG --> Written device data:
{'Date_Time': '21-12-20_15:28:48', 'XiaomiAirPurifier2_aqi': 22, 'XiaomiAirPurifier2_humidity': 49, 'XiaomiAirPurifier2_temperature': 22.2, 'XiaomiAirPurifier2_fan_rpm': 347} to:
/home/logs/Purifier/Purifier_2020-12-21_15:23:48.csv
21-12-20_15:30:01.963, [ds18b20_logger.py/__write_temperatures] -- DEBUG --> Room [02162cffffff] -> data read time: 5.30 ms. Read error counter: 0
21-12-20_15:30:02.016, [device_data_csv_writer.py/__write_data_to_file] -- DEBUG --> Written device data:
{'Date_Time': '21-12-20_15:30:01', 'Room_temperature': '24.45'} to:
/home/logs/Temperature/Temperature_2020-12-21_15:25:01.csv
```

## Tasmota_2020-12-21_15:23:47.csv
```
Date_Time,LanbergPlug_ac_power,LanbergPlug_ac_voltage,LanbergPlug_ac_current,BlitzwolfPlug_ac_power,BlitzwolfPlug_ac_voltage,BlitzwolfPlug_ac_current
21-12-20_15:23:46,27,212,0.217,48,212,0.345
21-12-20_15:27:47,27,212,0.215,46,212,0.341
21-12-20_15:31:48,27,212,0.217,49,213,0.337
21-12-20_15:35:49,28,212,0.219,49,212,0.338
```

## Purifier_2020-12-21_15:23:48.csv
```
Date_Time,XiaomiAirPurifier2_aqi,XiaomiAirPurifier2_humidity,XiaomiAirPurifier2_temperature,XiaomiAirPurifier2_fan_rpm
21-12-20_15:23:46,32,49,22.1,700
21-12-20_15:28:48,22,49,22.2,347
21-12-20_15:33:54,24,49,22.2,347
21-12-20_15:39:00,35,49,22.2,347
```

## Temperature_2020-12-21_15:25:01.csv
```
Date_Time,Room_temperature
21-12-20_15:25:01,24.5
21-12-20_15:30:01,24.45
21-12-20_15:35:02,24.46
21-12-20_15:40:02,24.44
```
