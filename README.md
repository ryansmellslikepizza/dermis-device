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

# 📦 Installing systemd Services (DERMIS Device)

To run the Dermis supervisor automatically at boot, you must install the `.service` file into the system’s service directory and enable it through `systemd`.

Follow this workflow whenever you first set up a device or update a service file.

---

## ✅ **1. Ensure the service file exists in your repo**

Your repository should contain:

```
systemd/dermis-supervisor.service
```

This file is tracked in Git, but systemd cannot see it yet.

---

## ✅ **2. Copy the service file into the systemd directory**

On the Raspberry Pi:

```bash
sudo cp systemd/dermis-supervisor.service /etc/systemd/system/
```

Systemd only loads services from `/etc/systemd/system/` or `/lib/systemd/system/`.

---

## ✅ **3. Reload systemd to recognize the new service**

```bash
sudo systemctl daemon-reload
```

This must be run any time you add or modify a `.service` file.

---

## ✅ **4. Enable the service so it runs at boot**

```bash
sudo systemctl enable dermis-supervisor.service
```

This tells systemd to automatically start the service every time the device boots.

---

## ✅ **5. (Optional) Start the service immediately**

```bash
sudo systemctl start dermis-supervisor.service
```

Useful for testing without rebooting.

---

## ✅ **6. Check logs to verify the service is running**

```bash
journalctl -u dermis-supervisor.service -f
```

This streams real-time logs from the supervisor, similar to output from `npm start`.

---

## 🔄 Updating the service file

If you change the `.service` file in your repo:

1. Copy it again:

   ```bash
   sudo cp systemd/dermis-supervisor.service /etc/systemd/system/
   ```

2. Reload systemd:

   ```bash
   sudo systemctl daemon-reload
   ```

3. Restart the service:

   ```bash
   sudo systemctl restart dermis-supervisor.service
   ```