Perfect, that’s totally doable — and you *don’t* need a “real” router for your supervisor script to be happy.

What you actually need is:

* something that **acts as a Wi-Fi AP**,
* gives the Pi an IP via DHCP, and
* responds to **ping** so your `wifi_check_host` test passes.

The Pico 2 W in AP mode can do exactly that.

---

## Overview

You’ll do:

1. **Pico 2 W** → run as Wi-Fi **Access Point** (`TEST-ROUTER`).
2. **Raspberry Pi** → connect to `TEST-ROUTER` like it’s a normal router.
3. Point `wifi_check_host` in `config.json` at the Pico’s IP (typically `192.168.4.1`).
4. Your `supervisor.py` ping check will see “online” and start the mirror app.

No actual internet required.

---

## Step 1 – Put Pico 2 W in AP mode (MicroPython)

Flash MicroPython to the Pico 2 W (via Raspberry Pi Imager or Thonny), then create a file on the Pico called `main.py` with:

```python
import network
import socket
import time

SSID = "TEST-ROUTER"
PASSWORD = "12345678"

# Start Wi-Fi Access Point
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

print("AP active?", ap.active())
print("AP config:", ap.ifconfig())  # ('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1')

# Optional tiny HTTP server, not strictly needed for ping
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

html = """HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n
<html><body><h1>Pico 2 W Test Router</h1></body></html>"""

print("Web server listening on 0.0.0.0:80")

while True:
    cl, addr = s.accept()
    print("Client connected from", addr)
    _ = cl.recv(1024)  # read request (ignore content)
    cl.send(html)
    cl.close()
```

When this runs, the Pico:

* broadcasts `TEST-ROUTER`
* gives clients IPs like `192.168.4.x`
* sits at `192.168.4.1` and responds to ping automatically
* serves a simple page at `http://192.168.4.1/`

---

## Step 2 – Connect the Raspberry Pi to the Pico AP

On the Pi (your dermis-device), run:

```bash
nmcli dev wifi connect "TEST-ROUTER" password "12345678"
```

or use the desktop Wi-Fi menu and select `TEST-ROUTER`.

Verify:

```bash
ip addr show wlan0
ping 192.168.4.1
```

You should see replies from the Pico.

---

## Step 3 – Point your supervisor at the Pico

In `config.json` on the Pi, change:

```json
{
  "device_mode": "dev",
  "wifi_check_host": "192.168.4.1",
  "wifi_check_timeout_sec": 3,
  "wifi_connect_timeout_sec": 30,
  "ble_advertise_timeout_sec": 900
}
```

Now your `supervisor.py`’s `wifi_is_online()` ping test will ping the Pico instead of 8.8.8.8.

From the Pi’s perspective, it looks like:

* Wi-Fi is configured ✅
* Network is reachable ✅
* “Router” is alive ✅

So the supervisor will treat this exactly like being on a real Wi-Fi network and move into the “RUNNING” state.

---

## Tiny sanity check flow

1. Power Pico → it starts `TEST-ROUTER` AP (`192.168.4.1`).
2. Boot Raspberry Pi:

   * `nmcli` connects it to `TEST-ROUTER`.
   * `supervisor.py` runs:

     * sees Wi-Fi configured,
     * pings `192.168.4.1`,
     * gets replies,
     * starts `dermis-mirror.service`.
3. You can tail logs on the Pi and tweak supervisor logic with a totally controlled “fake router.”

---

If you want, next we can wire in a quick **`wifi_helpers.py`** function that connects to `TEST-ROUTER` via `nmcli` automatically so you don’t even have to do it by hand during tests.
