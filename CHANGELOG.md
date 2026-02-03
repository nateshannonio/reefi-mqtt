# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-03

### Added
- Initial release
- MQTT Discovery support for Home Assistant
- Multi-device support (up to 3 ReeFi lights)
- Automatic Fahrenheit to Celsius temperature conversion
- Monitoring of all 9 LED channels
- System health monitoring (temperature, power, fan speed)
- Mode and moon phase tracking
- Systemd service integration
- Graceful shutdown handling
- Configurable polling interval
- Only publish on change (reduces MQTT traffic)
- Comprehensive logging
- YAML configuration (easier than Python)
- Auto-update system with systemd timer
- Complete setup script with template-based service installation
- Git hooks for secret detection
- CI/CD workflows for testing and releases
- Complete documentation

### Features
- Poll ReeFi HTTP API every 10 seconds (configurable)
- Publish to MQTT with Home Assistant auto-discovery
- Support for multiple devices
- Automatic reconnection on network failures
- Retain messages for state persistence
- Availability topic for online/offline status
- Daily auto-updates from GitHub (optional)
- Timestamped config backups before updates

### Scripts
- `scripts/setup.sh` - One-time setup with dependency installation
- `scripts/update.sh` - Auto-update from GitHub with service restart
- `reefi-mqtt-update.timer` - Systemd timer for daily updates (3 AM)
- `reefi-mqtt-update.service` - Systemd service for update execution

## [Unreleased]

### Planned
- Control support (brightness, profiles) via MQTT
- Web interface for configuration
- Statistics and history tracking
- Alert notifications
- Support for additional ReeFi models
- Docker container
- Home Assistant add-on
