# scanner.py

import subprocess
import asyncio
import requests
import time
from bleak import BleakScanner

baseline_ssids = set()
latest_speed = {"download": 0, "upload": 0, "ping": -1}
latest_scan = {
    "wifi": [],
    "rogue_aps": [],
    "ble": [],
    "ble_status": False,
    "internet": {"connected": False, "speed": latest_speed},
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

def scan_wifi():
    try:
        res = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True, text=True, timeout=10
        )
        networks, current = [], None
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("SSID") and ":" in line:
                current = line.split(":",1)[1].strip()
            elif line.startswith("Signal") and current:
                p = int(line.split(":",1)[1].strip().replace("%",""))
                rssi = (p/2)-100
                networks.append((current, round(rssi,1)))
                current = None
        return networks
    except:
        return []

async def scan_ble():
    devices = []
    def cb(dev, adv): devices.append((dev.name or "Unknown", dev.address, adv.rssi))
    try:
        s = BleakScanner(cb)
        await s.start(); await asyncio.sleep(5); await s.stop()
    except:
        pass
    return devices

def detect_rogue(current_ssids):
    global baseline_ssids
    return current_ssids - baseline_ssids

def has_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

def background_speed():
    global latest_speed
    import speedtest
    while True:
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            st.download(); st.upload()
            r = st.results
            latest_speed = {
                "download": round(r.download/1e6,2),
                "upload": round(r.upload/1e6,2),
                "ping": round(r.ping,2)
            }
        except:
            latest_speed = {"download":0,"upload":0,"ping":-1}
        time.sleep(15)

def background_scan():
    global baseline_ssids, latest_scan, latest_speed
    while True:
        wifi = scan_wifi()
        ssids = {s for s,_ in wifi}
        if not baseline_ssids:
            baseline_ssids = ssids.copy()
        rogue = list(detect_rogue(ssids))
        try:
            ble = asyncio.run(scan_ble()); ble_ok=True
        except:
            ble, ble_ok = [], False
        inet = has_internet()
        latest_scan = {
            "wifi": wifi,
            "rogue_aps": rogue,
            "ble": ble,
            "ble_status": ble_ok,
            "internet": {"connected": inet, "speed": latest_speed.copy()},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print("✔ Scan updated:", latest_scan)
        time.sleep(15)

def get_latest():
    return latest_scan
