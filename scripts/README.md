# Scripts Directory

Utility scripts for ReeFi MQTT Bridge installation and maintenance.

## Scripts

### setup.sh
**One-time setup script** - Run this after cloning the repository.

```bash
./scripts/setup.sh
```

**What it does:**
- Installs system dependencies (Python, git)
- Installs Python packages from requirements.txt
- Creates systemd service from template
- Sets up auto-update timer
- Configures git hooks
- Creates config.yaml from template

**When to use:** Initial installation on a new system.

---

### update.sh
**Auto-update script** - Updates code from GitHub and restarts service.

```bash
./scripts/update.sh
```

**What it does:**
- Fetches latest changes from GitHub
- Backs up config.yaml (timestamped)
- **Automatically cleans up old backups (keeps last 10)**
- Pulls updates
- Updates Python dependencies
- Restarts reefi-mqtt service

**When to use:** 
- Manually: When you want to pull latest changes
- Automatically: Scheduled daily via reefi-mqtt-update.timer

---

### cleanup-backups.sh
**Backup cleanup script** - Removes old config backups.

```bash
# Keep last 10 backups (default)
./scripts/cleanup-backups.sh

# Keep last 20 backups
./scripts/cleanup-backups.sh 20

# Keep last 5 backups
./scripts/cleanup-backups.sh 5
```

**What it does:**
- Lists all config.yaml backup files
- Shows which files will be deleted
- Prompts for confirmation
- Deletes oldest backups, keeping specified number

**When to use:**
- Manually clean up backups
- Change retention policy
- Free up disk space

**Note:** The update.sh script automatically keeps the last 10 backups, so manual cleanup is rarely needed.

---

### Auto-Update System

The auto-update system keeps your ReeFi MQTT Bridge up to date automatically.

**Components:**
- `reefi-mqtt-update.service` - Systemd service that runs update.sh
- `reefi-mqtt-update.timer` - Timer that schedules daily updates

**Schedule:**
- Runs daily at 3:00 AM
- Runs 5 minutes after boot (if system was off at 3 AM)
- Persistent (catches up if missed)

**Enable auto-updates:**
```bash
sudo systemctl enable reefi-mqtt-update.timer
sudo systemctl start reefi-mqtt-update.timer
```

**Check status:**
```bash
# Timer status
sudo systemctl status reefi-mqtt-update.timer

# View timer schedule
systemctl list-timers reefi-mqtt-update.timer

# View update logs
journalctl -u reefi-mqtt-update.service -n 50
```

**Disable auto-updates:**
```bash
sudo systemctl stop reefi-mqtt-update.timer
sudo systemctl disable reefi-mqtt-update.timer
```

---

## Installation Methods

### Method 1: Setup Script (Recommended)
For first-time installation in a git repository:

```bash
git clone https://github.com/YOUR_USERNAME/reefi-mqtt.git
cd reefi-mqtt
./scripts/setup.sh
```

### Method 2: Legacy Install Script
For installation from a tarball (no git):

```bash
tar -xzf reefi-mqtt-v1.0.0.tar.gz
cd reefi-mqtt
sudo ./install.sh
```

**Note:** The install.sh script is deprecated and will redirect to setup.sh if run from a git repository.

---

## Systemd Service Templates

The systemd service files use placeholders that are replaced during setup:

**Placeholders:**
- `REEFI_USER` - Current user (e.g., homeassistant, pi)
- `REEFI_REPO_DIR` - Repository directory (e.g., /home/pi/reefi-mqtt)

**Service files:**
- `reefi-mqtt.service` - Main service (in root directory)
- `reefi-mqtt-update.service` - Update service (in scripts/)
- `reefi-mqtt-update.timer` - Update timer (in scripts/)

---

## Manual Installation

If you prefer to install manually:

1. **Install dependencies:**
   ```bash
   sudo apt-get install python3 python3-pip git
   pip3 install -r requirements.txt --break-system-packages
   ```

2. **Create config:**
   ```bash
   cp config.example.yaml config.yaml
   nano config.yaml
   ```

3. **Install service:**
   ```bash
   # Replace placeholders in service file
   sed -e "s|REEFI_USER|$USER|g" \
       -e "s|REEFI_REPO_DIR|$PWD|g" \
       reefi-mqtt.service | sudo tee /etc/systemd/system/reefi-mqtt.service
   
   sudo systemctl daemon-reload
   sudo systemctl enable reefi-mqtt
   sudo systemctl start reefi-mqtt
   ```

4. **Optional: Enable auto-updates:**
   ```bash
   sed -e "s|REEFI_USER|$USER|g" \
       -e "s|REEFI_REPO_DIR|$PWD|g" \
       scripts/reefi-mqtt-update.service | sudo tee /etc/systemd/system/reefi-mqtt-update.service
   
   sudo cp scripts/reefi-mqtt-update.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable reefi-mqtt-update.timer
   sudo systemctl start reefi-mqtt-update.timer
   ```

---

## Troubleshooting

### Setup fails
```bash
# Check script is executable
chmod +x scripts/setup.sh

# Run with debug output
bash -x scripts/setup.sh
```

### Service won't start after update
```bash
# Check service status
sudo systemctl status reefi-mqtt

# View recent logs
journalctl -u reefi-mqtt -n 50

# Test config manually
python3 reefi_mqtt.py
```

### Auto-update not running
```bash
# Check timer is enabled
systemctl is-enabled reefi-mqtt-update.timer

# Check timer schedule
systemctl list-timers reefi-mqtt-update.timer

# Manually trigger update
sudo systemctl start reefi-mqtt-update.service
```

### Config was overwritten by update
```bash
# Restore from backup
cp config.yaml.backup-YYYYMMDD-HHMMSS config.yaml
sudo systemctl restart reefi-mqtt

# List available backups
ls -lht config.yaml.backup-*

# View most recent backup
cat config.yaml.backup-$(ls -t config.yaml.backup-* | head -1)
```

**Note:** The update script automatically keeps the last 10 backups and deletes older ones.

### Too many backup files
```bash
# Manually clean up (keep last 10)
./scripts/cleanup-backups.sh

# Keep different number (e.g., 5)
./scripts/cleanup-backups.sh 5

# Check disk usage
du -sh config.yaml.backup-*
```

---

## Security Considerations

### Auto-Update Safety

**Pros:**
- Always get security fixes
- Always get new features
- No manual intervention needed

**Cons:**
- Untested updates could break things
- Config changes might require manual edits

**Recommendation:**
- Enable auto-updates for production systems
- Monitor logs after updates: `journalctl -u reefi-mqtt-update.service`
- Keep config backups: automatically created in `config.yaml.backup-*`

### Disabling Auto-Updates

If you prefer manual control:
```bash
sudo systemctl disable reefi-mqtt-update.timer
sudo systemctl stop reefi-mqtt-update.timer
```

Then update manually when ready:
```bash
./scripts/update.sh
```

---

## Files Created by Scripts

**By setup.sh:**
- `/etc/systemd/system/reefi-mqtt.service`
- `/etc/systemd/system/reefi-mqtt-update.service`
- `/etc/systemd/system/reefi-mqtt-update.timer`
- `config.yaml` (if doesn't exist)

**By update.sh:**
- `config.yaml.backup-YYYYMMDD-HHMMSS` (timestamped backups)
- **Retention:** Last 10 backups are kept, older ones are automatically deleted

**Backup retention examples:**
```bash
# If you have 15 backups, oldest 5 are deleted automatically
config.yaml.backup-20250201-030000  # Deleted
config.yaml.backup-20250202-030000  # Deleted
config.yaml.backup-20250203-030000  # Deleted
config.yaml.backup-20250204-030000  # Deleted
config.yaml.backup-20250205-030000  # Deleted
config.yaml.backup-20250206-030000  # Kept (10th oldest)
config.yaml.backup-20250207-030000  # Kept
...
config.yaml.backup-20250215-030000  # Kept (newest)
```

---

## See Also

- [Installation Guide](../docs/INSTALLATION.md) - Detailed installation instructions
- [README](../README.md) - Project overview
- [CONTRIBUTING](../CONTRIBUTING.md) - Development guidelines
