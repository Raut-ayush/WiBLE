import subprocess
import threading
import platform
import socket
import time
import asyncio
from datetime import datetime
from flask import Flask, render_template, redirect, request, jsonify

try:
    from bleak import BleakScanner
except ImportError:
    BleakScanner = None

try:
    import speedtest
except ImportError:
    speedtest = None

app = Flask(__name__)

# -------------------------- Globals -------------------------- #
scan_data = {
    "wifi": [],
    "rogue_aps": [],
    "ble": [],
    "ble_status": True,
    "internet": {"connected": False, "speed": {"download": 0, "upload": 0, "ping": -1}},
    "timestamp": "Never"
}

baseline_ssids = set()


# ---------------------- Scan Functions ---------------------- #
def scan_wifi():
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        lines = output.splitlines()

        wifi_list = []
        ssid = None
        for line in lines:
            line = line.strip()
            if line.startswith("SSID ") and ":" in line:
                ssid = line.split(":", 1)[1].strip()
            elif line.startswith("Signal") and ssid:
                strength = line.split(":", 1)[1].strip().replace("%", "")
                try:
                    rssi = round(int(strength) / 2 - 100, 1)
                    wifi_list.append((ssid, rssi))
                except:
                    continue
        return wifi_list
    except Exception as e:
        print("⚠️ Wi-Fi scan failed:", e)
        return []


async def scan_ble_async():
    try:
        devices = await BleakScanner.discover(timeout=6.0)
        return [(d.name or "Unknown", d.address, d.rssi) for d in devices]
    except Exception as e:
        print("⚠️ BLE scan failed:", e)
        return []


def scan_ble():
    if not BleakScanner:
        scan_data["ble_status"] = False
        return []

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scan_ble_async())
        scan_data["ble_status"] = True

        print(f"🔵 BLE Devices: {len(result)} found")
        return result
    except Exception as e:
        scan_data["ble_status"] = False
        print("⚠️ BLE error:", e)
        return []


def check_internet_speed():
    if not speedtest:
        return {"connected": False, "speed": {"download": 0, "upload": 0, "ping": -1}}
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download()
        upload = st.upload()
        ping = st.results.ping
        return {
            "connected": True,
            "speed": {
                "download": round(download / 1e6, 2),
                "upload": round(upload / 1e6, 2),
                "ping": round(ping, 2)
            }
        }
    except Exception as e:
        print("⚠️ Speed test failed:", e)
        return {"connected": False, "speed": {"download": 0, "upload": 0, "ping": -1}}


# -------------------- Main Scan --------------------- #
def run_one_scan():
    global baseline_ssids

    wifi = scan_wifi()
    print("📶 Wi-Fi Results:", wifi)

    if not baseline_ssids:
        baseline_ssids.update([ssid for ssid, _ in wifi])
    rogue_aps = [ssid for ssid, _ in wifi if ssid not in baseline_ssids]
    print("🧨 Rogue APs:", rogue_aps)

    ble = scan_ble()

    internet = check_internet_speed()
    print("🌐 Internet Speed:", internet)

    scan_data.update({
        "wifi": wifi,
        "rogue_aps": rogue_aps,
        "ble": ble,
        "internet": internet,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    print("📦 Updated scan_data:", scan_data)


def background_scanner():
    while True:
        run_one_scan()
        print("✔ Background scan complete\n")
        time.sleep(10)


# ----------------------- Flask Routes ------------------------ #

# ----------------------- Flask Routes ------------------------ #
@app.route("/")
def index():
    return render_template("index.html", data=scan_data)


@app.route("/api/status")
def api_status():
    """Returns the current scan data as JSON for the frontend."""
    return jsonify(scan_data)


@app.route("/rescan", methods=["POST"])
def rescan():
    print("🔁 Manual rescan triggered...")
    # Run scan in background to avoid blocking
    threading.Thread(target=run_one_scan, daemon=True).start()
    if request.is_json:
        return jsonify({"status": "scanning_started"})
    return redirect("/")


@app.route("/connect", methods=["POST"])
def connect_wifi():
    """Connect to a Wi-Fi network using netsh."""
    data = request.get_json()
    ssid = data.get("ssid")
    password = data.get("password")

    if not ssid:
        return jsonify({"status": "error", "message": "SSID required"}), 400

    print(f"🔌 Attempting to connect to {ssid}...")
    
    # Check if profile exists; if not, we'd need to create an XML profile.
    # For simplicity, we'll assume the user might need to create a profile or we use a basic one.
    # WARNING: 'netsh wlan connect' usually requires a profile to exist. 
    # Creating a profile programmatically via Python is complex (requires XML).
    # We will try a simpler approach if possible, or just attempt connection if known.
    # However, standard netsh connect requires name=ProfileName.
    
    # For a robust "Connect" feature with password, we need to generate an XML profile.
    # We'll use a helper to generate that XML.
    
    try:
        profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        
        # Save XML to temp file
        import os
        xml_path = f"temp_profile_{ssid}.xml"
        with open(xml_path, "w") as f:
            f.write(profile_xml)
            
        # Add profile
        add_cmd = subprocess.run(
            ["netsh", "wlan", "add", "profile", f"filename={xml_path}"],
            capture_output=True, text=True
        )
        
        # Cleanup XML
        os.remove(xml_path)
        
        if "is added on interface" not in add_cmd.stdout and "updated on interface" not in add_cmd.stdout:
             print("❌ Failed to add profile:", add_cmd.stdout)
             return jsonify({"status": "error", "message": "Failed to configure network profile"}), 500

        # Connect
        connect_cmd = subprocess.run(
            ["netsh", "wlan", "connect", f"name={ssid}"],
            capture_output=True, text=True
        )
        
        if "Connection request was completed successfully" in connect_cmd.stdout:
             return jsonify({"status": "success", "message": f"Connecting to {ssid}..."})
        else:
             return jsonify({"status": "error", "message": "Connection request failed"}), 500

    except Exception as e:
        print("⚠️ Connection failed:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/disconnect", methods=["POST"])
def disconnect_wifi():
    """Disconnect from the current Wi-Fi."""
    try:
        subprocess.run(["netsh", "wlan", "disconnect"], check=True)
        return jsonify({"status": "success", "message": "Disconnected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/forget", methods=["POST"])
def forget_wifi():
    """Delete a Wi-Fi profile."""
    data = request.get_json()
    ssid = data.get("ssid")
    if not ssid:
        return jsonify({"status": "error", "message": "SSID required"}), 400
        
    try:
        subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"], check=True)
        return jsonify({"status": "success", "message": f"Forgot {ssid}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# ---------------------------- Main --------------------------- #
if __name__ == "__main__":
    print("🛰️ WiBLE Scanner Running...")

    run_one_scan()  # Synchronous first scan

    threading.Thread(target=background_scanner, daemon=True).start()

    app.run(debug=True)
