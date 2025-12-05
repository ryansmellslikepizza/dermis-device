#!/bin/bash
# install_services.sh
# Install or update systemd service files from the dermis-device repo.

set -e

# Must run as root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root:"
  echo "    sudo ./install_services.sh"
  exit 1
fi

echo "🔧 Installing Dermis systemd services..."

# Directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Repo root = one directory above /scripts
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_DIR="$REPO_ROOT/systemd"

echo "📁 Script directory:    $SCRIPT_DIR"
echo "📁 Repo root:           $REPO_ROOT"
echo "📁 Service file folder: $SERVICE_DIR"
echo ""

# Service files you expect in repo/systemd/
SERVICE_FILES=(
  "dermis-supervisor.service"
  "dermis-ble.service"
  "dermis-mirror.service"
)

for svc in "${SERVICE_FILES[@]}"; do
  SRC="$SERVICE_DIR/$svc"
  DEST="/etc/systemd/system/$svc"

  if [ -f "$SRC" ]; then
    echo "➡️  Installing $svc → /etc/systemd/system/"
    cp "$SRC" "$DEST"
  else
    echo "⚠️  Skipping $svc (not found in $SERVICE_DIR)"
  fi
done

echo ""
echo "🔄 Reloading systemd..."
systemctl daemon-reload

echo ""
echo "🚀 Enabling + restarting services..."
for svc in "${SERVICE_FILES[@]}"; do
  if [ -f "/etc/systemd/system/$svc" ]; then
    echo "   ✓ Enabling $svc"
    systemctl enable "$svc" || true

    echo "   ↻ Restarting $svc"
    systemctl restart "$svc" || true
  fi
done

echo ""
echo "✅ Done! Services installed and active."
