#!/usr/bin/env python3
"""
Dermis Boot Supervisor
Decides whether to start BLE provisioning or the core mirror app.
"""

import json
import time
import subprocess
from pathlib import Path

CONFIG_PATH = Path("/opt/dermis/config.json")
STATE_PATH  = Path("/opt/dermis/state.json")

def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "device_mode": "prod",
        "wifi_check_host": "8.8.8.8",
        "wifi_check_timeout_sec": 3,
        "wifi_connect_timeout_sec": 30,
        "ble_advertise_timeout_sec": 900
    }

def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2))

def run(cmd):
    return subprocess.run(cmd, shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          text=True)

def wifi_is_configured():
    res = run("nmcli -t -f NAME,TYPE connection show")
    return any(":wifi" in line for line in res.stdout.splitlines())

def wifi_is_online(host, timeout):
    cmd = f"ping -c 1 -W {timeout} {host}"
    return run(cmd).returncode == 0

def try_connect_wifi(cfg):
    timeout = cfg["wifi_connect_timeout_sec"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        if wifi_is_online(cfg["wifi_check_host"], cfg["wifi_check_timeout_sec"]):
            return True
    return False

def start_service(name):
    run(f"systemctl start {name}")

def stop_service(name):
    run(f"systemctl stop {name}")

def set_led(pattern):
    run(f"/opt/dermis/led_helper.sh {pattern}")

def main():
    cfg = load_config()
    state = {
        "last_boot_ts": int(time.time()),
        "last_state": "BOOTING"
    }
    save_state(state)

    set_led("boot")

    # ---------------------------------------------------------
    # DEV MODE (skip logic, run everything)
    # ---------------------------------------------------------
    if cfg["device_mode"] == "dev":
        start_service("dermis-ble.service")
        start_service("dermis-mirror.service")
        set_led("online")
        state["last_state"] = "RUNNING_DEV"
        save_state(state)
        return

    # ---------------------------------------------------------
    # PROD MODE
    # ---------------------------------------------------------
    state["last_state"] = "CHECK_WIFI"
    save_state(state)

    if wifi_is_configured() and try_connect_wifi(cfg):
        start_service("dermis-mirror.service")
        set_led("online")
        state["last_state"] = "RUNNING"
        save_state(state)
        return

    # Wi-Fi missing or failed → BLE provisioning
    state["last_state"] = "PROVISIONING"
    save_state(state)

    set_led("setup")
    start_service("dermis-ble.service")

    timeout = cfg["ble_advertise_timeout_sec"]
    start_time = time.time()

    while True:
        if wifi_is_configured() and wifi_is_online(cfg["wifi_check_host"], cfg["wifi_check_timeout_sec"]):
            stop_service("dermis-ble.service")
            start_service("dermis-mirror.service")
            set_led("online")
            state["last_state"] = "RUNNING"
            save_state(state)
            return

        if time.time() - start_time > timeout:
            set_led("error")

        time.sleep(3)


if __name__ == "__main__":
    main()
