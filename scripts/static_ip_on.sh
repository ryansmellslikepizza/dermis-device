#!/usr/bin/env bash
set -euo pipefail

CONN="ATT7GnJaRm"
IP="192.168.1.50/24"
GW="192.168.1.1"
DNS="192.168.1.1 8.8.8.8"

echo "Enabling STATIC IP on connection: $CONN"
sudo nmcli connection modify "$CONN" \
  ipv4.method manual \
  ipv4.addresses "$IP" \
  ipv4.gateway "$GW" \
  ipv4.dns "$DNS"

echo "Cycling connection to apply changes..."
sudo nmcli connection down "$CONN" || true
sudo nmcli connection up "$CONN"

echo "Done. Current IPv4 for $CONN:"
nmcli -g IP4.ADDRESS,IP4.GATEWAY,IP4.DNS connection show "$CONN" | sed '/^$/d'
ip route | sed -n '1,5p'
