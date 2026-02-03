#!/bin/bash
# scripts/update.sh
#
# Auto-update script for ReeFi MQTT Bridge
# Pulls latest changes from GitHub and restarts service if needed
#
# Called by reefi-mqtt-update.service (daily at 3 AM)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "ReeFi MQTT Bridge - Auto Update"
echo "=========================================="
echo "Time: $(date)"
echo "Repo: $REPO_DIR"
echo ""

cd "$REPO_DIR"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "ERROR: Not a git repository. Skipping update."
    exit 1
fi

# Fetch latest changes
echo "Fetching latest changes from GitHub..."
git fetch origin

# Check if there are updates
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "Already up to date!"
    exit 0
fi

echo "Updates available!"
echo "Local:  $LOCAL"
echo "Remote: $REMOTE"
echo ""

# Backup current config
if [ -f "config.yaml" ]; then
    echo "Backing up config.yaml..."
    BACKUP_FILE="config.yaml.backup-$(date +%Y%m%d-%H%M%S)"
    cp config.yaml "$BACKUP_FILE"
    echo "  Created: $BACKUP_FILE"
    
    # Clean up old backups (keep last 10)
    echo "Cleaning up old backups (keeping last 10)..."
    ls -t config.yaml.backup-* 2>/dev/null | tail -n +11 | xargs -r rm -f
    
    REMAINING=$(ls config.yaml.backup-* 2>/dev/null | wc -l)
    echo "  Backups remaining: $REMAINING"
fi

# Pull changes
echo "Pulling changes..."
git pull origin main

# Update Python dependencies
echo ""
echo "Updating Python dependencies..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
pip3 install -r requirements.txt

# Check if service is active
if systemctl is-active --quiet reefi-mqtt; then
    echo ""
    echo "Restarting reefi-mqtt service..."
    sudo systemctl restart reefi-mqtt
    
    # Wait a moment
    sleep 2
    
    # Check if it started successfully
    if systemctl is-active --quiet reefi-mqtt; then
        echo "✓ Service restarted successfully"
    else
        echo "✗ Service failed to restart!"
        echo "Check logs: journalctl -u reefi-mqtt -n 50"
        exit 1
    fi
else
    echo ""
    echo "reefi-mqtt service is not running, skipping restart"
fi

echo ""
echo "=========================================="
echo "Update complete!"
echo "=========================================="
echo ""
echo "Updated to: $(git rev-parse --short HEAD)"
echo "View changes: git log --oneline -5"
echo ""
