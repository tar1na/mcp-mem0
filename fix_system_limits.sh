#!/bin/bash

# Fix System Limits for MCP-Mem0 Service
# This script addresses the "Too many open files" error

set -e

echo "🔧 Fixing System Limits for MCP-Mem0 Service"
echo "=============================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

echo ""
echo "📊 Current System Limits:"
echo "Current ulimit -n: $(ulimit -n)"
echo "System file-max: $(cat /proc/sys/fs/file-max)"

echo ""
echo "🔧 Updating System Limits..."

# Update /etc/security/limits.conf
echo "Updating /etc/security/limits.conf..."
cat >> /etc/security/limits.conf << EOF

# MCP-Mem0 Service Limits
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
EOF

# Update systemd limits
echo "Updating systemd limits..."
mkdir -p /etc/systemd/system/mcp-mem0.service.d
cat > /etc/systemd/system/mcp-mem0.service.d/limits.conf << EOF
[Service]
LimitNOFILE=65536
LimitNPROC=65536
EOF

# Reload systemd and restart service
echo "Reloading systemd configuration..."
systemctl daemon-reload

echo ""
echo "✅ System limits updated successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Restart the mcp-mem0 service:"
echo "   sudo systemctl restart mcp-mem0"
echo ""
echo "2. Check service status:"
echo "   sudo systemctl status mcp-mem0"
echo ""
echo "3. Monitor logs for any remaining issues:"
echo "   sudo journalctl -u mcp-mem0 -f"
echo ""
echo "4. Verify the new limits are active:"
echo "   sudo systemctl show mcp-mem0 | grep LimitNOFILE"
echo ""
echo "🔄 The new limits will take effect after a reboot or service restart."

