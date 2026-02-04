# reefi-mqtt

MQTT bridge for ReeFi Uno Pro 2.1 LED aquarium lights with Home Assistant MQTT Discovery support.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## Overview

This bridge polls ReeFi Uno Pro LED lights via their HTTP API and publishes the data to MQTT, enabling seamless integration with Home Assistant through MQTT Discovery.

### Features

- ✅ **MQTT Discovery** - Devices auto-appear in Home Assistant
- ✅ **Multi-device support** - Control multiple ReeFi lights
- ✅ **Efficient updates** - Only publishes when values change
- ✅ **Auto-reconnect** - Handles network interruptions gracefully
- ✅ **Complete monitoring** - All 9 LED channels, temperature, power, fan speed
- ✅ **Temperature conversion** - Automatic Fahrenheit to Celsius
- ✅ **Systemd service** - Auto-start on boot with proper logging
- ✅ **Production-ready** - Error handling, logging, graceful shutdown

## Monitored Data

For each ReeFi device:
- **Temperature** (°C, with F→C conversion)
- **Power consumption** (W)
- **Fan speed** (RPM)
- **Current mode** (Day/Peak/Moon/etc)
- **Moon phase** (%)
- **9 LED channels** (CH0-CH8: UV, violets, blues, lime, amber, whites)

## Requirements

- Python 3.7 or higher
- MQTT broker (Mosquitto recommended)
- Home Assistant with MQTT integration
- ReeFi Uno Pro 2.1 LED light(s) on your network

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/reefi-mqtt.git
cd reefi-mqtt

# Install Python dependencies
pip3 install -r requirements.txt

# Copy and edit configuration
cp config.example.py config.py
nano config.py

# Test the bridge
python3 reefi_mqtt.py

# Install as service (optional)
sudo ./install.sh
```

### Detailed Installation

See [INSTALLATION.md](INSTALLATION.md) for complete step-by-step instructions.

## Configuration

Edit `config.py` to match your setup:

```python
# MQTT Broker
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_USERNAME = None  # Set if authentication required
MQTT_PASSWORD = None

# ReeFi Devices
REEFI_DEVICES = [
    {
        'id': 'reefi_uno_pro_1',
        'name': 'Reefi Uno Pro 1',
        'ip': '192.168.1.100',
        'enabled': True
    },
    {
        'id': 'reefi_uno_pro_2',
        'name': 'Reefi Uno Pro 2',
        'ip': '192.168.1.101',
        'enabled': True
    }
]

# Polling interval (seconds)
POLL_INTERVAL = 10
```

## Home Assistant Integration

### Automatic Discovery

Devices automatically appear in Home Assistant:

1. Go to **Settings** → **Devices & Services**
2. Find **MQTT** integration
3. Your ReeFi devices will be listed with all sensors

### Manual Configuration (Optional)

If you prefer manual configuration, see [HOME_ASSISTANT.md](docs/HOME_ASSISTANT.md).

## MQTT Topics

### State Topics

```
homeassistant/sensor/reefi_uno_pro_1/temperature/state
homeassistant/sensor/reefi_uno_pro_1/power/state
homeassistant/sensor/reefi_uno_pro_1/fan_rpm/state
homeassistant/sensor/reefi_uno_pro_1/mode/state
homeassistant/sensor/reefi_uno_pro_1/ch0/state
homeassistant/sensor/reefi_uno_pro_1/ch1/state
...
homeassistant/sensor/reefi_uno_pro_1/ch8/state
```

### Discovery Topics

```
homeassistant/sensor/reefi_uno_pro_1/temperature/config
homeassistant/sensor/reefi_uno_pro_1/power/config
...
```

### Availability Topic

```
homeassistant/sensor/reefi_bridge/availability
```

## Running as a Service

### Systemd Service

```bash
# Install service
sudo ./install.sh

# Check status
sudo systemctl status reefi-mqtt

# View logs
sudo journalctl -u reefi-mqtt -f

# Restart
sudo systemctl restart reefi-mqtt
```

### Manual Start

```bash
python3 reefi_mqtt.py
```

## Monitoring

### Check Bridge Status

```bash
# Service status
sudo systemctl status reefi-mqtt

# Live logs
sudo journalctl -u reefi-mqtt -f

# Recent logs
sudo journalctl -u reefi-mqtt -n 100
```

### Monitor MQTT Messages

```bash
# All ReeFi messages
mosquitto_sub -h localhost -t "homeassistant/sensor/reefi_#" -v

# Specific device
mosquitto_sub -h localhost -t "homeassistant/sensor/reefi_uno_pro_1/+/state" -v

# Discovery messages
mosquitto_sub -h localhost -t "homeassistant/sensor/+/+/config" -v
```

## Troubleshooting

### Bridge Won't Connect to MQTT

```bash
# Check MQTT broker is running
sudo systemctl status mosquitto

# Test MQTT connectivity
mosquitto_pub -h localhost -t "test" -m "hello"
mosquitto_sub -h localhost -t "test"
```

### Can't Reach ReeFi Device

```bash
# Test HTTP connectivity
curl http://192.168.1.100/info4
curl http://192.168.1.100/now.cfg

# Ping device
ping 192.168.1.100
```

### Sensors Not Appearing in Home Assistant

1. Check MQTT integration is configured in HA
2. Check bridge is running: `sudo systemctl status reefi-mqtt`
3. Check MQTT discovery messages: `mosquitto_sub -h localhost -t "homeassistant/#" -v`
4. Restart Home Assistant

For more troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Architecture

```
ReeFi Devices (HTTP API)
         ↓
  reefi-mqtt Bridge
         ↓
    MQTT Broker
         ↓
   Home Assistant
```

The bridge:
1. Polls ReeFi HTTP API every 10 seconds (configurable)
2. Parses temperature, power, channels, etc.
3. Publishes changes to MQTT
4. Uses MQTT Discovery for auto-configuration

## Hybrid Control Approach

This bridge handles **monitoring** via MQTT. For **control** (brightness, profiles), you can still use HTTP REST commands in Home Assistant:

```yaml
rest_command:
  reefi_set_brightness:
    url: "http://192.168.1.100/Lrequests?master={{ brightness }}"
    method: GET

automation:
  - alias: "Set ReeFi Brightness"
    trigger:
      - platform: state
        entity_id: input_number.reefi_brightness
    action:
      - service: rest_command.reefi_set_brightness
        data:
          brightness: "{{ states('input_number.reefi_brightness') | int }}"
```

See [HOME_ASSISTANT.md](docs/HOME_ASSISTANT.md) for complete examples.

## Development

### Running Tests

```bash
python3 -m pytest tests/
```

### Code Style

```bash
# Format code
black reefi_mqtt.py

# Lint
pylint reefi_mqtt.py
```

## API Documentation

ReeFi Uno Pro 2.1 HTTP API endpoints:

- `GET /info4` - System information (temperature, power, fan)
- `GET /now.cfg` - Current state (channels, mode, moon phase)
- `GET /Lrequests?master=X` - Set master brightness (0-100)
- `GET /Lrequests?pindex=X` - Set profile (0-19)
- `GET /Lrequests?chX=Y` - Set channel value (0-1023)

See [API.md](docs/API.md) for complete documentation.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [jebao-mqtt](https://github.com/nateshannonio/jebao-mqtt)
- Thanks to the Home Assistant community
- ReeFi for their excellent LED lights

## Related Projects

- [jebao-mqtt](https://github.com/nateshannonio/jebao-mqtt) - MQTT bridge for Jebao wave makers
- [home-assistant](https://github.com/home-assistant/core) - Open source home automation

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/reefi-mqtt/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/reefi-mqtt/discussions)
- 📧 **Email**: your.email@example.com

## Screenshots

### Home Assistant Devices

![ReeFi Device in Home Assistant](docs/images/ha-device.png)

### Dashboard

![ReeFi Dashboard](docs/images/dashboard.png)

---

**Star this repository if you find it useful!** ⭐
