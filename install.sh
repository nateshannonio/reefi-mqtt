#!/bin/bash

# ReeFi MQTT Bridge Installation Script
# This script is deprecated - use scripts/setup.sh instead

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=========================================="
echo "ReeFi MQTT Bridge Installer"
echo -e "==========================================${NC}"
echo ""
echo -e "${YELLOW}NOTE: This install.sh is deprecated.${NC}"
echo -e "Please use the new setup script instead:"
echo ""
echo -e "  ${GREEN}./scripts/setup.sh${NC}"
echo ""
echo "The new setup script provides:"
echo "  - Auto-update functionality"
echo "  - Better error handling"
echo "  - Template-based systemd service installation"
echo "  - Git hooks configuration"
echo ""
read -p "Run new setup script now? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    exec ./scripts/setup.sh
fi

echo ""
echo "Canceled. To install manually, run:"
echo "  ./scripts/setup.sh"
echo ""
