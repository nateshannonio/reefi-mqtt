# Backup Management Summary

Comprehensive backup retention and cleanup system for ReeFi MQTT Bridge.

## ✅ Automatic Backup System

### When Backups Are Created
Every time `update.sh` runs (daily at 3 AM via timer), a backup is created:
```bash
config.yaml.backup-20250203-030000
```

### Automatic Cleanup
**Retention Policy:** Keep last **10 backups**, delete older ones

**Implementation:**
```bash
# In update.sh
ls -t config.yaml.backup-* 2>/dev/null | tail -n +11 | xargs -r rm -f
```

This command:
1. Lists all backups sorted by time (newest first)
2. Skips the first 10 (`tail -n +11`)
3. Deletes the rest

### Disk Space Impact

**Example calculation:**
- Config file size: ~2 KB
- 10 backups: ~20 KB
- Negligible disk usage

**With 365 daily updates WITHOUT cleanup:**
- 365 backups × 2 KB = ~730 KB
- Still minimal, but cleanup keeps it tidy

## 📊 Backup Lifecycle

### Daily Update Scenario

**Day 1:**
```
config.yaml.backup-20250201-030000  (1 backup)
```

**Day 10:**
```
config.yaml.backup-20250201-030000
config.yaml.backup-20250202-030000
...
config.yaml.backup-20250210-030000  (10 backups)
```

**Day 11 (cleanup triggers):**
```
config.yaml.backup-20250201-030000  ❌ DELETED
config.yaml.backup-20250202-030000  ✅ Kept (now 10th oldest)
...
config.yaml.backup-20250211-030000  ✅ Kept (newest)
```

**Day 15:**
```
config.yaml.backup-20250206-030000  ✅ Kept (10th oldest)
config.yaml.backup-20250207-030000  ✅ Kept
...
config.yaml.backup-20250215-030000  ✅ Kept (newest)
```

## 🔧 Manual Cleanup

### cleanup-backups.sh Script

**Default usage (keep 10):**
```bash
./scripts/cleanup-backups.sh
```

**Custom retention:**
```bash
# Keep last 5 backups
./scripts/cleanup-backups.sh 5

# Keep last 20 backups
./scripts/cleanup-backups.sh 20

# Keep last 30 backups (one month)
./scripts/cleanup-backups.sh 30
```

### Script Features

1. **Shows what will be deleted:**
   ```
   Total backups found: 25
   Keeping most recent: 10
   Backups to delete: 15
   
   Files to be deleted:
     config.yaml.backup-20250201-030000 (2.1K)
     config.yaml.backup-20250202-030000 (2.0K)
     ...
   ```

2. **Confirms before deletion:**
   ```
   Proceed with deletion? (y/n)
   ```

3. **Shows results:**
   ```
   Cleanup complete!
   Backups remaining: 10
   
   Most recent backups:
     20250215-030000 (2.1K)
     20250214-030000 (2.0K)
     ...
   ```

## 📋 Backup Commands Reference

### List all backups
```bash
ls -lht config.yaml.backup-*
```

### Count backups
```bash
ls config.yaml.backup-* 2>/dev/null | wc -l
```

### View most recent backup
```bash
cat config.yaml.backup-$(ls -t config.yaml.backup-* | head -1)
```

### Restore from backup
```bash
# Interactive: choose from list
ls -t config.yaml.backup-*

# Restore specific backup
cp config.yaml.backup-20250215-030000 config.yaml
sudo systemctl restart reefi-mqtt

# Restore most recent
cp config.yaml.backup-$(ls -t config.yaml.backup-* | head -1) config.yaml
sudo systemctl restart reefi-mqtt
```

### Check disk usage
```bash
# All backups
du -sh config.yaml.backup-*

# Total
du -ch config.yaml.backup-* | tail -1
```

### Manual cleanup (keep last 5)
```bash
ls -t config.yaml.backup-* | tail -n +6 | xargs rm -f
```

## ⚙️ Customizing Retention Policy

### Change default retention in update.sh

Edit `scripts/update.sh`:

```bash
# Change from 10 to 20
ls -t config.yaml.backup-* 2>/dev/null | tail -n +21 | xargs -r rm -f
```

### Disable automatic cleanup

Comment out cleanup in `scripts/update.sh`:

```bash
# # Clean up old backups (keep last 10)
# echo "Cleaning up old backups (keeping last 10)..."
# ls -t config.yaml.backup-* 2>/dev/null | tail -n +11 | xargs -r rm -f
```

Then manage manually with `cleanup-backups.sh`

## 🔍 Monitoring Backups

### Check backup status in logs
```bash
journalctl -u reefi-mqtt-update.service -n 50 | grep -i backup
```

Example output:
```
Feb 03 03:00:05 server update.sh[1234]: Backing up config.yaml...
Feb 03 03:00:05 server update.sh[1234]:   Created: config.yaml.backup-20250203-030000
Feb 03 03:00:05 server update.sh[1234]: Cleaning up old backups (keeping last 10)...
Feb 03 03:00:05 server update.sh[1234]:   Backups remaining: 10
```

### Add cron job for backup monitoring
```bash
# Create monitoring script
cat > ~/check-reefi-backups.sh << 'EOF'
#!/bin/bash
cd ~/reefi-mqtt
COUNT=$(ls config.yaml.backup-* 2>/dev/null | wc -l)
if [ "$COUNT" -gt 15 ]; then
    echo "WARNING: $COUNT config backups found (expected ~10)"
fi
EOF
chmod +x ~/check-reefi-backups.sh

# Add to cron (weekly check)
(crontab -l 2>/dev/null; echo "0 12 * * 0 ~/check-reefi-backups.sh") | crontab -
```

## 🎯 Best Practices

### Recommended Settings

1. **Keep 10 backups (default)** - Provides ~10 days of history
2. **Daily auto-updates** - Creates one backup per day
3. **Manual cleanup as needed** - Use `cleanup-backups.sh` if changing policy

### When to Increase Retention

Consider keeping more backups if:
- You make frequent manual config changes
- You want longer rollback history
- Disk space is not a concern

**Example: Keep 30 backups (one month)**
```bash
# In update.sh, change to:
tail -n +31
```

### When to Decrease Retention

Consider fewer backups if:
- Disk space is very limited
- Config rarely changes
- You have external backups

**Example: Keep 5 backups**
```bash
# In update.sh, change to:
tail -n +6
```

## 💾 External Backup Recommendations

For critical deployments, also backup config externally:

```bash
# Backup to remote server
scp config.yaml user@backup-server:/backups/reefi-mqtt/

# Backup to git (private repo)
git add config.yaml.backup-*
git commit -m "Config backups $(date +%Y-%m)"
git push backup-remote

# Backup to cloud storage
rclone copy config.yaml remote:reefi-mqtt/backups/
```

## 📊 Summary

| Feature | Value |
|---------|-------|
| **Default retention** | 10 backups |
| **Cleanup frequency** | Every update (daily) |
| **Backup size** | ~2 KB each |
| **Total disk usage** | ~20 KB (10 backups) |
| **Manual cleanup** | `./scripts/cleanup-backups.sh` |
| **Customizable** | Yes, edit update.sh |

**Result:** Automatic, hands-off backup management with minimal disk usage! ✅
