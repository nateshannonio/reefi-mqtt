#!/bin/bash
# scripts/cleanup-backups.sh
#
# Clean up old config backups
# By default keeps last 10 backups, configurable

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Number of backups to keep (default: 10)
KEEP_COUNT=${1:-10}

cd "$REPO_DIR"

echo "=========================================="
echo "ReeFi MQTT - Backup Cleanup"
echo "=========================================="
echo ""

# Count existing backups
TOTAL=$(ls config.yaml.backup-* 2>/dev/null | wc -l)

if [ "$TOTAL" -eq 0 ]; then
    echo "No backup files found."
    exit 0
fi

echo "Total backups found: $TOTAL"
echo "Keeping most recent: $KEEP_COUNT"
echo ""

if [ "$TOTAL" -le "$KEEP_COUNT" ]; then
    echo "Nothing to clean up (total <= keep count)."
    exit 0
fi

# Calculate how many to delete
DELETE_COUNT=$((TOTAL - KEEP_COUNT))
echo "Backups to delete: $DELETE_COUNT"
echo ""

# Show files to be deleted
echo "Files to be deleted:"
ls -t config.yaml.backup-* 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | while read file; do
    SIZE=$(du -h "$file" | cut -f1)
    echo "  $file ($SIZE)"
done

echo ""
read -p "Proceed with deletion? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Canceled."
    exit 0
fi

# Delete old backups
echo "Deleting old backups..."
ls -t config.yaml.backup-* 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | xargs -r rm -f

REMAINING=$(ls config.yaml.backup-* 2>/dev/null | wc -l)
echo ""
echo "Cleanup complete!"
echo "Backups remaining: $REMAINING"
echo ""
echo "Most recent backups:"
ls -t config.yaml.backup-* 2>/dev/null | head -5 | while read file; do
    SIZE=$(du -h "$file" | cut -f1)
    DATE=$(echo "$file" | sed 's/config.yaml.backup-//')
    echo "  $DATE ($SIZE)"
done
