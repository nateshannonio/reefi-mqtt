# ReeFi MQTT Repository Overview

Complete GitHub repository structure following the jebao-mqtt pattern.

## 📦 Repository Structure

```
reefi-mqtt/
├── README.md                 # Main documentation (badges, features, overview)
├── QUICKSTART.md            # 5-minute setup guide
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore patterns
├── requirements.txt         # Python dependencies
├── install.sh              # Automated installation script
├── reefi_mqtt.py           # Main bridge application
├── config.example.py       # Example configuration file
└── docs/                   # Documentation directory
    └── INSTALLATION.md     # Detailed installation guide
```

## 📄 File Descriptions

### Core Files

**reefi_mqtt.py** (14 KB)
- Main application code
- MQTT Discovery implementation
- HTTP API polling
- Temperature conversion
- Error handling and logging
- Graceful shutdown

**config.example.py** (3 KB)
- Example configuration template
- Fully commented
- All options explained
- Copy to `config.py` to use

**requirements.txt**
```
paho-mqtt>=1.6.1
requests>=2.28.0
```

### Installation

**install.sh** (executable)
- Automated installation script
- Creates `/opt/reefi-mqtt`
- Installs systemd service
- Sets up permissions
- Enables auto-start

### Documentation

**README.md** (8 KB)
- Project overview with badges
- Feature list
- Quick installation
- MQTT topics reference
- Troubleshooting basics
- Links to detailed docs

**QUICKSTART.md** (2 KB)
- Minimal steps to get running
- Essential configuration only
- Common commands
- Quick troubleshooting

**docs/INSTALLATION.md** (7 KB)
- Detailed step-by-step installation
- Multiple installation methods
- Advanced configuration
- Complete troubleshooting
- Upgrade/uninstall instructions

**CHANGELOG.md**
- Version history
- Release notes
- Planned features

### Configuration

**LICENSE**
- MIT License
- Open source

**.gitignore**
- Excludes config.py (contains passwords)
- Python cache files
- IDE files
- OS files

## 🎯 Key Features

### Matches jebao-mqtt Pattern

✅ **Similar Structure**
- Main Python script
- Separate config file
- Install script
- Systemd service
- Documentation directory

✅ **Configuration Style**
- Device list in config
- MQTT broker settings
- Enable/disable per device
- Polling interval

✅ **Installation**
- One-command install
- Service auto-start
- Proper logging

### Improvements Over HTTP

✅ **MQTT Discovery** - Auto-configuration in HA
✅ **Device Grouping** - All sensors per device
✅ **Efficient Updates** - Only publish changes
✅ **Availability** - Online/offline status
✅ **Consistent** - Matches your Jebao setup

## 🚀 Quick Setup

```bash
# Clone
git clone https://github.com/yourusername/reefi-mqtt.git
cd reefi-mqtt

# Configure
cp config.example.py config.py
nano config.py

# Install
sudo ./install.sh
```

## 📊 MQTT Topics

### State Topics (per device)
```
homeassistant/sensor/reefi_uno_pro_1/temperature/state
homeassistant/sensor/reefi_uno_pro_1/power/state
homeassistant/sensor/reefi_uno_pro_1/fan_rpm/state
homeassistant/sensor/reefi_uno_pro_1/mode/state
homeassistant/sensor/reefi_uno_pro_1/moon_phase/state
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

### Availability
```
homeassistant/sensor/reefi_bridge/availability (online/offline)
```

## 🔧 Service Management

```bash
# Status
sudo systemctl status reefi-mqtt

# Start/Stop/Restart
sudo systemctl start reefi-mqtt
sudo systemctl stop reefi-mqtt
sudo systemctl restart reefi-mqtt

# Enable/Disable (auto-start)
sudo systemctl enable reefi-mqtt
sudo systemctl disable reefi-mqtt

# Logs
sudo journalctl -u reefi-mqtt -f
sudo journalctl -u reefi-mqtt -n 100
```

## 📈 Monitoring

```bash
# All ReeFi MQTT messages
mosquitto_sub -h localhost -t "homeassistant/sensor/reefi_#" -v

# Specific device
mosquitto_sub -h localhost -t "homeassistant/sensor/reefi_uno_pro_1/+/state" -v

# Discovery messages
mosquitto_sub -h localhost -t "homeassistant/sensor/+/+/config" -v

# All messages (debug)
mosquitto_sub -h localhost -t "#" -v
```

## 🏠 Home Assistant Integration

### Automatic (Recommended)

Devices auto-appear after bridge starts:

1. **Settings** → **Devices & Services** → **MQTT**
2. Find "Reefi Uno Pro 1" (or your device name)
3. All sensors are automatically created

### Manual (Optional)

See `docs/HOME_ASSISTANT.md` for:
- Control configuration (brightness, profiles)
- Dashboard examples
- Automation examples
- Hybrid MQTT + HTTP setup

## 🆚 Comparison with HTTP Setup

| Feature | HTTP (Old) | MQTT (New) |
|---------|-----------|-----------|
| **Installation** | Edit YAML | Run install script |
| **Configuration** | YAML templates | Python config file |
| **Discovery** | Manual | Automatic |
| **Updates** | Poll every 10-30s | Poll + only on change |
| **Grouping** | Manual | Automatic |
| **Consistency** | Mixed | All MQTT |
| **Service** | HA polling | Standalone service |
| **Monitoring** | HA logs | Systemd journal |
| **Debugging** | curl | mosquitto_sub |

## 🔄 Migration Path

### Keep HTTP for Control

```yaml
# HTTP commands still work!
rest_command:
  reefi_set_brightness:
    url: "http://192.168.1.100/Lrequests?master={{ brightness }}"
```

### Use MQTT for Monitoring

All sensors come from MQTT auto-discovery.

### Remove Old HTTP Sensors

Delete from your `packages/reefi.yaml`:
- `sensor:` platform: rest sections
- `template:` sensor sections

Keep:
- `rest_command:` sections
- `input_number:` sliders
- `input_select:` dropdowns
- `automation:` control automations

## 📦 Distribution

### GitHub Release

1. Tag version: `git tag v1.0.0`
2. Push tags: `git push --tags`
3. Create release on GitHub
4. Attach `reefi-mqtt-v1.0.0.tar.gz`

### Installation from Release

```bash
wget https://github.com/yourusername/reefi-mqtt/archive/v1.0.0.tar.gz
tar -xzf v1.0.0.tar.gz
cd reefi-mqtt-1.0.0
sudo ./install.sh
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📝 Development

### Testing

```bash
# Run manually with debug logging
python3 reefi_mqtt.py

# Check config syntax
python3 -c "import config; print('Config OK')"

# Test MQTT connection
mosquitto_pub -h localhost -t "test" -m "hello"
```

### Code Style

```bash
# Format
black reefi_mqtt.py

# Lint
pylint reefi_mqtt.py
```

## 🎉 Ready to Publish

The repository is complete and ready for:

✅ GitHub upload
✅ First release (v1.0.0)
✅ Public use
✅ Community contributions

All files follow the jebao-mqtt pattern and include:
- Comprehensive README
- Quick start guide
- Detailed documentation
- Automated installation
- Example configuration
- MIT License
- Proper .gitignore

## 📦 Files to Upload to GitHub

```bash
.gitignore
CHANGELOG.md
LICENSE
QUICKSTART.md
README.md
config.example.py
install.sh (executable)
reefi_mqtt.py (executable)
requirements.txt
docs/INSTALLATION.md
```

**DO NOT upload:**
- `config.py` (contains passwords - in .gitignore)
- `__pycache__/` (in .gitignore)
- `*.pyc` (in .gitignore)
- `*.log` (in .gitignore)

---

**Repository is production-ready!** 🚀
