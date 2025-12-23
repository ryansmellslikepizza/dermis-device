#!/usr/bin/env bash
set -euo pipefail

CONN="ATT7GnJaRm"

echo "Disabling STATIC IP (switching to DHCP) on connection: $CONN"
sudo nmcli connection modify "$CONN" \
  ipv4.method auto \
  ipv4.addresses "" \
  ipv4.gateway "" \
  ipv4.dns ""

echo "Cycling connection to apply changes..."
sudo nmcli connection down "$CONN" || true
sudo nmcli connection up "$CONN"

echo "Done. Current IPv4 for $CONN:"
nmcli -g IP4.ADDRESS,IP4.GATEWAY,IP4.DNS connection show "$CONN" | sed '/^$/d'
ip route | sed -n '1,5p'
