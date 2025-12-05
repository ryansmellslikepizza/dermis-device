#!/usr/bin/env python3
"""
DERMIS DEVICE — Boot Supervisor
-------------------------------
This script runs at boot (via systemd) and decides whether the device should:

1. Start BLE provisioning   (no Wi-Fi / failed connection)
2. Start the mirror app     (Wi-Fi works)
3. Run DEV mode             (always start BLE + mirror)

It also updates LED state patterns and writes boot state for debugging.
"""

import json
import time
import subprocess
import logging
import sys
from pathlib import Path

# -------------------------------------------------------------------
# File paths
# -------------------------------------------------------------------
CONFIG_PATH = Path("/opt/dermis/config.json")
STATE_PATH  = Path("/opt/dermis/state.json")

# -------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("dermis-supervisor")

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
def load_config():
    """Load config.json or return defaults."""
    if CONFIG_PATH.exists():
        log.info("Loading config from %s", CONFIG_PATH)
        return json.loads(CONFIG_PATH.read_text())
    
    log.warning("Config file missing. Using defaults.")
    return {
        "device_mode": "prod",
        "wifi_check_host": "8.8.8.8",
        "wifi_check_timeout_sec": 3,
        "wifi_connect_timeout_sec": 30,
        "ble_advertise_timeout_sec": 900
    }


def save_state(state):
    """Persist state.json for debugging."""
    try:
        STATE_PATH.write_text(json.dumps(state, indent=2))
        log.info("State updated: %s", state)
    except Exception as e:
        log.error("Failed to write state.json: %s", e)


def run(cmd):
    """Run a shell command and return subprocess result."""
    log.debug("Running command: %s", cmd)
    return subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def wifi_is_configured():
    """Return True if NetworkManager has any Wi-Fi connection profiles."""
    result = run("nmcli -t -f NAME,TYPE connection show")
    configured = any(":wifi" in line for line in result.stdout.splitlines())
    log.info("Wi-Fi configured? %s", configured)
    return configured


def wifi_is_online(host, timeout):
    """Return True if ping succeeds to the check host."""
    cmd = f"ping -c 1 -W {timeout} {host}"
    result = run(cmd)
    success = (result.returncode == 0)
    log.info("Ping %s → %s", host, success)
    return success


def try_connect_wifi(cfg):
    """Try connecting to Wi-Fi for up to wifi_connect_timeout_sec."""
    log.info("Attempting Wi-Fi connection for up to %s seconds...",
             cfg["wifi_connect_timeout_sec"])

    deadline = time.time() + cfg["wifi_connect_timeout_sec"]

    while time.time() < deadline:
        time.sleep(2)
        if wifi_is_online(cfg["wifi_check_host"], cfg["wifi_check_timeout_sec"]):
            log.info("Wi-Fi connection SUCCESS")
            return True

    log.warning("Wi-Fi connection FAILED within timeout.")
    return False


def start_service(name):
    """Start a systemd service."""
    log.info("Starting service: %s", name)
    run(f"systemctl start {name}")


def stop_service(name):
    """Stop a systemd service."""
    log.info("Stopping service: %s", name)
    run(f"systemctl stop {name}")


def set_led(pattern):
    """Set LED state pattern."""
    log.info("Setting LED pattern: %s", pattern)
    run(f"/opt/dermis/led_helper.sh {pattern}")


# -------------------------------------------------------------------
# Main Logic
# -------------------------------------------------------------------
def main():
    log.info("=== Dermis Supervisor Boot Start ===")

    cfg = load_config()
    state = {
        "last_boot_ts": int(time.time()),
        "last_state": "BOOTING"
    }
    save_state(state)

    # LED: boot up indicator
    set_led("boot")

    # -------------------------------------------------------------------
    # DEV MODE — always run BLE + mirror for debugging
    # -------------------------------------------------------------------
    if cfg["device_mode"] == "dev":
        log.info("DEV MODE ACTIVE — starting BLE + Mirror immediately.")
        start_service("dermis-ble.service")
        start_service("dermis-mirror.service")
        set_led("online")
        state["last_state"] = "RUNNING_DEV"
        save_state(state)
        return

    # -------------------------------------------------------------------
    # PROD MODE — check Wi-Fi first
    # -------------------------------------------------------------------
    log.info("PROD MODE — checking Wi-Fi state.")
    state["last_state"] = "CHECK_WIFI"
    save_state(state)

    wifi_ok = wifi_is_configured() and try_connect_wifi(cfg)

    if wifi_ok:
        # Start mirror app
        log.info("Wi-Fi SUCCESS — starting mirror app.")
        start_service("dermis-mirror.service")
        set_led("online")
        state["last_state"] = "RUNNING"
        save_state(state)
        return

    # -------------------------------------------------------------------
    # Wi-Fi NOT OK → enter provisioning mode
    # -------------------------------------------------------------------
    log.warning("Wi-Fi missing or failed. Entering BLE provisioning mode.")
    state["last_state"] = "PROVISIONING"
    save_state(state)

    set_led("setup")
    start_service("dermis-ble.service")

    timeout = cfg["ble_advertise_timeout_sec"]
    start_time = time.time()

    while True:
        # Check if user has provisioned Wi-Fi
        if wifi_is_configured() and wifi_is_online(cfg["wifi_check_host"], cfg["wifi_check_timeout_sec"]):
            log.info("Wi-Fi provisioning successful — switching to RUNNING mode.")
            stop_service("dermis-ble.service")
            start_service("dermis-mirror.service")
            set_led("online")
            state["last_state"] = "RUNNING"
            save_state(state)
            return

        # Timeout → keep provisioning but set LED = error
        if time.time() - start_time > timeout:
            log.error("BLE provisioning timeout exceeded — LED=error but continuing loop.")
            set_led("error")

        time.sleep(3)


if __name__ == "__main__":
    main()
