# Dermis Device Firmware (V1 Skeleton)

This repository contains the firmware for the Dermis Smart Beauty Mirror (V1).

## Components

### supervisor.py
Boot manager that:
- checks Wi-Fi
- starts BLE provisioning if needed
- starts mirror core app
- drives LED status

### ble_provisioning.py
Stub BLE server (to be replaced with GATT implementation).

### mirror_app.py
Stub for the main device logic (LEDs, camera, uploads).

### led_helper.sh
Shell helper for LED patterns.

### wifi_helpers.py
Wi-Fi scan + credential-setting helpers.

### systemd services
Unit files that allow the device to auto-start on boot.

---

## Modes

- **DEV mode:** `device_mode = "dev"`  
  Starts both BLE + mirror app regardless of Wi-Fi.

- **PROD mode:** `device_mode = "prod"`  
  Wi-Fi first → BLE provisioning only if needed.

---

## Next Steps
1. Implement BLE GATT service.
2. Add real Wi-Fi scanning + provisioning.
3. Integrate LED GPIO control.
4. Add camera + upload logic to mirror_app.py.
