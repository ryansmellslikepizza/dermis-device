#!/bin/bash
# LED state helper script
# Usage: ./led_helper.sh boot|setup|online|error

PATTERN="$1"

echo "[LED] Setting LED pattern: $PATTERN"

# Add actual GPIO operations here later
# For now, just echo so supervisor doesn’t break
