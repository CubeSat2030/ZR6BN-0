# install_hotspot_deps.sh

#!/bin/bash
# Kabot-1 Hotspot Dependency Installer
# Run with: sudo ./install_hotspot_deps.sh

set -e

echo "🔧 Updating package list..."
sudo apt update

echo "📦 Installing hotspot dependencies..."
sudo apt install -y hostapd dnsmasq iproute2 net-tools logrotate python3 python3-pip

echo "✅ Dependencies installed successfully."
echo " - hostapd: Wi-Fi Access Point service"
echo " - dnsmasq: DHCP/DNS service"
echo " - iproute2: provides 'ip' command"
echo " - net-tools: debugging (ifconfig, etc.)"
echo " - logrotate: manage growing logs"
echo " - python3 + pip: runtime for scripts"

echo "🚀 Kabot-1 hotspot environment ready!"

