# Installation Guide

Complete step-by-step installation guide for ReeFi MQTT Bridge.

## Prerequisites

### Required
- Python 3.7 or higher
- MQTT broker (Mosquitto recommended)
- Home Assistant with MQTT integration configured
- ReeFi Uno Pro 2.1 LED light(s) on your network

### Recommended
- Linux system (Raspberry Pi, Ubuntu, Debian)
- Systemd for service management
- Basic command line knowledge

## Quick Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/reefi-mqtt.git
cd reefi-mqtt
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install paho-mqtt requests
```

### 3. Configure

```bash
cp config.example.py config.py
nano config.py
```

Update these settings:
- `MQTT_BROKER` - Your MQTT broker IP/hostname
- `MQTT_USERNAME` and `MQTT_PASSWORD` - If authentication required
- `REEFI_DEVICES` - Your ReeFi device IPs and names

### 4. Test

```bash
python3 reefi_mqtt.py
```

You should see:
```
2025-01-31 12:00:00 - reefi-mqtt - INFO - Starting ReeFi MQTT Bridge
2025-01-31 12:00:00 - reefi-mqtt - INFO - Connecting to MQTT broker at localhost:1883
2025-01-31 12:00:00 - reefi-mqtt - INFO - Connected to MQTT broker successfully
2025-01-31 12:00:00 - reefi-mqtt - INFO - Publishing MQTT discovery messages
2025-01-31 12:00:00 - reefi-mqtt - INFO - Starting polling loop (interval: 10s)
```

Press Ctrl+C to stop.

### 5. Install as Service

```bash
sudo ./install.sh
```

## Detailed Installation

### Option 1: Automated Installation (Recommended)

```bash
# Download and run install script
git clone https://github.com/yourusername/reefi-mqtt.git
cd reefi-mqtt
cp config.example.py config.py
nano config.py  # Edit configuration
sudo ./install.sh
```

The install script will:
- Install Python dependencies
- Create `/opt/reefi-mqtt` directory
- Copy files to install directory
- Create systemd service
- Enable and start service

### Option 2: Manual Installation

#### Step 1: Create Installation Directory

```bash
sudo mkdir -p /opt/reefi-mqtt
```

#### Step 2: Copy Files

```bash
sudo cp reefi_mqtt.py /opt/reefi-mqtt/
sudo cp config.example.py /opt/reefi-mqtt/
sudo cp config.py /opt/reefi-mqtt/  # If you've configured it
```

#### Step 3: Set Permissions

```bash
sudo chmod +x /opt/reefi-mqtt/reefi_mqtt.py
sudo chown -R homeassistant:homeassistant /opt/reefi-mqtt
```

#### Step 4: Create Service File

```bash
sudo nano /etc/systemd/system/reefi-mqtt.service
```

Paste:
```ini
[Unit]
Description=ReeFi MQTT Bridge
After=network.target mosquitto.service
Wants=mosquitto.service

[Service]
Type=simple
User=homeassistant
Group=homeassistant
WorkingDirectory=/opt/reefi-mqtt
ExecStart=/usr/bin/python3 /opt/reefi-mqtt/reefi_mqtt.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Step 5: Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable reefi-mqtt
sudo systemctl start reefi-mqtt
```

## Configuration

### Basic Configuration

Edit `config.py`:

```python
# MQTT Broker
MQTT_BROKER = '192.168.1.50'  # Your broker IP
MQTT_PORT = 1883
MQTT_USERNAME = 'mqtt_user'    # If required
MQTT_PASSWORD = 'mqtt_pass'

# ReeFi Devices
REEFI_DEVICES = [
    {
        'id': 'reefi_uno_pro_1',
        'name': 'Display Tank Light',
        'ip': '192.168.1.100',
        'enabled': True
    }
]

# Polling
POLL_INTERVAL = 10  # seconds
```

### Advanced Configuration

#### SSL/TLS

```python
MQTT_USE_TLS = True
MQTT_CA_CERTS = '/path/to/ca.crt'
MQTT_PORT = 8883
```

#### Temperature Unit

```python
TEMPERATURE_UNIT = 'F'  # or 'C'
```

#### Logging

```python
LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = '/var/log/reefi-mqtt.log'
LOG_TO_CONSOLE = True
```

## Verification

### Check Service Status

```bash
sudo systemctl status reefi-mqtt
```

Expected output:
```
● reefi-mqtt.service - ReeFi MQTT Bridge
   Loaded: loaded (/etc/systemd/system/reefi-mqtt.service; enabled)
   Active: active (running) since ...
```

### Check Logs

```bash
sudo journalctl -u reefi-mqtt -f
```

### Check MQTT Messages

```bash
mosquitto_sub -h localhost -t "homeassistant/sensor/reefi_#" -v
```

You should see messages like:
```
homeassistant/sensor/reefi_uno_pro_1/temperature/state 31.1
homeassistant/sensor/reefi_uno_pro_1/power/state 15.0
homeassistant/sensor/reefi_uno_pro_1/ch0/state 56
```

### Check Home Assistant

1. Go to **Settings** → **Devices & Services**
2. Click **MQTT**
3. You should see your ReeFi devices listed

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status reefi-mqtt

# Check for errors
sudo journalctl -u reefi-mqtt -n 50
```

Common issues:
- **config.py missing**: Copy config.example.py to config.py
- **Permission denied**: Check file ownership
- **Python not found**: Install Python 3.7+
- **Dependencies missing**: Run `pip3 install -r requirements.txt`

### MQTT Connection Failed

```bash
# Test MQTT broker
mosquitto_pub -h YOUR_BROKER_IP -t "test" -m "hello"
```

Check:
- MQTT broker is running: `sudo systemctl status mosquitto`
- Broker IP/hostname is correct
- Username/password (if required)
- Firewall not blocking port 1883

### ReeFi Device Not Responding

```bash
# Test HTTP connection
curl http://REEFI_IP/info4
curl http://REEFI_IP/now.cfg
```

Check:
- ReeFi is powered on
- IP address is correct
- Same network/VLAN
- Firewall not blocking HTTP (port 80)

### Sensors Not Appearing in HA

1. Check MQTT integration is configured
2. Check discovery messages:
   ```bash
   mosquitto_sub -h localhost -t "homeassistant/+/+/+/config" -v
   ```
3. Restart Home Assistant
4. Check HA logs for MQTT errors

## Upgrading

### From Git

```bash
cd reefi-mqtt
git pull
sudo systemctl restart reefi-mqtt
```

### Manual Update

```bash
# Stop service
sudo systemctl stop reefi-mqtt

# Backup config
sudo cp /opt/reefi-mqtt/config.py ~/config.py.backup

# Copy new files
sudo cp reefi_mqtt.py /opt/reefi-mqtt/

# Restore config
sudo cp ~/config.py.backup /opt/reefi-mqtt/config.py

# Restart
sudo systemctl start reefi-mqtt
```

## Uninstalling

```bash
# Stop and disable service
sudo systemctl stop reefi-mqtt
sudo systemctl disable reefi-mqtt

# Remove service file
sudo rm /etc/systemd/system/reefi-mqtt.service
sudo systemctl daemon-reload

# Remove installation
sudo rm -rf /opt/reefi-mqtt

# Remove from Home Assistant
# Go to Settings → Devices & Services → MQTT
# Delete ReeFi devices
```

## Next Steps

- [Home Assistant Configuration](HOME_ASSISTANT.md)
- [API Documentation](API.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
