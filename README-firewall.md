
# Raspberry Pi Firewall Notes (SSH Safety)

This document records the firewall configuration and lessons learned during setup of the Esther V1 Raspberry Pi.

It exists because **SSH access was accidentally blocked** during development, and this must be avoided when setting up new Pis.

---

## Summary (TL;DR)

- A firewall **can block SSH even on a local network**
- On a headless Pi, this can **lock you out completely**
- SSH **must be explicitly allowed before enabling a firewall**
- Always test SSH **from another machine** before disconnecting a keyboard/monitor

---

## What happened

During setup, a firewall was enabled on the Raspberry Pi (likely via `ufw` or similar).

SSH (port 22) was **not explicitly allowed**, which caused:

- SSH connections to hang or fail
- No obvious error message on the Pi itself
- Risk of being locked out if running headless

Once SSH was blocked, access was only recoverable via:
- Physical keyboard + monitor
- Or disabling the firewall locally

---

## Firewall tools involved

Most likely tool:
- `ufw` (Uncomplicated Firewall)

Check with:

```bash
which ufw
sudo ufw status
```

---

## Correct firewall setup (SAFE ORDER)

### 1. Verify SSH is installed and running

```bash
sudo systemctl status ssh
```

If not installed:

```bash
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

---

### 2. BEFORE enabling the firewall — allow SSH

This step is **mandatory**.

```bash
sudo ufw allow ssh
```

or explicitly:

```bash
sudo ufw allow 22/tcp
```

---

### 3. Enable the firewall

```bash
sudo ufw enable
```

You should see a warning like:

> Command may disrupt existing ssh connections. Proceed with operation (y|n)?

Only proceed **if SSH is already allowed**.

---

### 4. Verify rules

```bash
sudo ufw status verbose
```

Expected minimum output:

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
22/tcp (v6)                ALLOW       Anywhere (v6)
```

---

## Recommended minimal rules for development Pi

For a development / prototype Pi on a trusted LAN:

```bash
sudo ufw allow ssh
sudo ufw allow 80/tcp    # optional (local web UI)
sudo ufw allow 443/tcp   # optional
sudo ufw enable
```

You do **not** need a firewall at all for early prototyping unless the Pi is exposed to the internet.

---

## How to recover if SSH is blocked

If you get locked out:

1. Connect keyboard + monitor
2. Log in locally
3. Disable or fix firewall:

```bash
sudo ufw disable
```

or:

```bash
sudo ufw allow ssh
sudo ufw reload
```

After that, SSH should work again.

---

## Best practices for future Pi setups

### ✅ Do this

* Always allow SSH **before** enabling firewall
* Keep a keyboard + HDMI cable nearby during setup
* Test SSH from another device **before going headless**
* Document firewall rules in the project repo (this file)

### ❌ Avoid this

* Enabling `ufw` on a headless Pi without SSH allowed
* Assuming “local network” means “safe by default”
* Forgetting which security changes were applied

---

## Recommendation for Dermis V1

For early hardware + camera development:

* **Firewall optional**
* SSH is more important than network hardening
* Add firewall later when:

  * Pi is stable
  * Boot process is automated
  * Remote recovery is easy

---

## Notes to future self

If SSH suddenly stops working:

1. Suspect firewall first
2. Ask: “Did I enable ufw?”
3. Check port 22 rules
4. Plug in a monitor if needed

This file exists so you don’t have to rediscover this the hard way.
