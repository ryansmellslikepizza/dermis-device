"""
Helper utilities for Wi-Fi scanning and connecting.
Later will be used from ble_provisioning.py
"""

import subprocess

def run(cmd):
    return subprocess.run(cmd, shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          text=True)

def scan_networks():
    # Placeholder scan
    print("[WIFI] Scanning for networks (stub)")
    return ["HomeWiFi", "Guest", "MyHotspot"]

def set_credentials(ssid, password):
    print(f"[WIFI] Writing credentials: SSID={ssid}, PASS={password} (stub)")
    # Later: write to wpa_supplicant or nmcli
