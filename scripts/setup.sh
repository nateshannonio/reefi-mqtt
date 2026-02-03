#!/bin/bash
# scripts/setup.sh
#
# Initial setup script for ReeFi MQTT Bridge
# Run once after cloning the repository
#
# Usage: ./scripts/setup.sh

set -e

echo "=========================================="
echo "ReeFi MQTT Bridge - Initial Setup"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CURRENT_USER="${SUDO_USER:-$USER}"

echo "User: $CURRENT_USER"
echo "Repo: $REPO_DIR"
echo ""

# ============================================
# Helper: install a systemd service from template
# Replaces REEFI_USER and REEFI_REPO_DIR placeholders
# ============================================
install_service() {
    local src="$1"
    local name=$(basename "$src")

    echo "  Installing $name..."
    sed -e "s|REEFI_USER|$CURRENT_USER|g" \
        -e "s|REEFI_REPO_DIR|$REPO_DIR|g" \
        "$src" | sudo tee "/etc/systemd/system/$name" > /dev/null
}

echo "1. Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends python3 python3-pip git

echo ""
echo "2. Installing Python dependencies..."
pip3 install -r "$REPO_DIR/requirements.txt" --break-system-packages 2>/dev/null || \
pip3 install -r "$REPO_DIR/requirements.txt"

echo ""
echo "3. Making scripts executable..."
chmod +x "$SCRIPT_DIR"/*.sh
chmod +x "$REPO_DIR/.githooks/pre-commit" 2>/dev/null || true

echo ""
echo "4. Installing systemd services..."
install_service "$REPO_DIR/reefi-mqtt.service"
install_service "$SCRIPT_DIR/reefi-mqtt-update.service"
sudo cp "$SCRIPT_DIR/reefi-mqtt-update.timer" /etc/systemd/system/
sudo systemctl daemon-reload

echo ""
echo "5. Setting up git hooks..."
cd "$REPO_DIR"
git config core.hooksPath .githooks 2>/dev/null || true

echo ""
echo "6. Creating config from template..."
if [ ! -f "$REPO_DIR/config.yaml" ]; then
    cp "$REPO_DIR/config.example.yaml" "$REPO_DIR/config.yaml"
    echo "  Created config.yaml from template"
else
    echo "  config.yaml already exists, skipping"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your configuration:"
echo "   nano $REPO_DIR/config.yaml"
echo ""
echo "2. Update device settings:"
echo "   - Set MQTT broker IP/hostname"
echo "   - Set ReeFi device IP addresses"
echo "   - Configure device names"
echo ""
echo "3. Test the bridge:"
echo "   python3 $REPO_DIR/reefi_mqtt.py"
echo ""
echo "4. Enable and start the service:"
echo "   sudo systemctl enable reefi-mqtt"
echo "   sudo systemctl start reefi-mqtt"
echo ""
echo "5. Enable auto-updates from GitHub (optional):"
echo "   sudo systemctl enable reefi-mqtt-update.timer"
echo "   sudo systemctl start reefi-mqtt-update.timer"
echo ""
echo "6. View status and logs:"
echo "   sudo systemctl status reefi-mqtt"
echo "   journalctl -u reefi-mqtt -f"
echo ""
echo "7. Monitor MQTT messages:"
echo "   mosquitto_sub -h localhost -t 'homeassistant/sensor/reefi_#' -v"
echo ""
