# Quick Start Guide

Get ReeFi MQTT Bridge running in 5 minutes!

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/reefi-mqtt.git
cd reefi-mqtt

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Configure
cp config.example.py config.py
nano config.py

# 4. Test it
python3 reefi_mqtt.py

# 5. Install as service (optional)
sudo ./install.sh
```

## Minimum Configuration

Edit `config.py`:

```python
MQTT_BROKER = '192.168.1.50'  # Your MQTT broker IP

REEFI_DEVICES = [
    {
        'id': 'reefi_uno_pro_1',
        'name': 'Main Tank Light',
        'ip': '192.168.1.100',  # Your ReeFi IP
        'enabled': True
    }
]
```

That's it! Save and run.

## What You Get

After starting the bridge:

1. **Automatic Discovery** - Devices appear in Home Assistant
2. **Real-time Monitoring** - Temperature, power, all 9 channels
3. **System Health** - Fan speed, mode, moon phase

## Check Home Assistant

1. Go to **Settings** → **Devices & Services**
2. Click **MQTT** integration
3. Your ReeFi device(s) will be listed

## Useful Commands

```bash
# Check status
sudo systemctl status reefi-mqtt

# View logs
sudo journalctl -u reefi-mqtt -f

# Restart
sudo systemctl restart reefi-mqtt

# Monitor MQTT
mosquitto_sub -h localhost -t "homeassistant/sensor/reefi_#" -v
```

## Next Steps

- Add control sliders: [HOME_ASSISTANT.md](docs/HOME_ASSISTANT.md)
- Create dashboards: See dashboard examples in repo
- Add more devices: Edit `config.py` and add to `REEFI_DEVICES`

## Troubleshooting

**Service won't start?**
```bash
sudo journalctl -u reefi-mqtt -n 50
```

**Can't reach ReeFi?**
```bash
curl http://REEFI_IP/info4
```

**MQTT not connecting?**
```bash
mosquitto_pub -h BROKER_IP -t "test" -m "hello"
```

For more help, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
