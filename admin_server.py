# admin_server.py
from flask import Flask, request, jsonify, render_template
import datetime

app = Flask(__name__)

connected_devices = []

@app.route("/")
def home():
    return "<h2>Admin Beacon Server Running</h2><a href='/reports'>View Reports</a>"

@app.route("/api/admin_report", methods=["POST"])
def receive_report():
    data = request.get_json()
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connected_devices.append(data)
    print("📥 Received beacon:", data)
    return jsonify({"status": "received"})

@app.route("/reports")
def reports():
    html = "<h2>🧾 Connected Devices</h2><ul>"
    for d in connected_devices:
        html += f"<li>{d['hostname']} ({d['platform']} {d['release']}) - {d['ip']} | MAC: {d['mac']}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(port=8080)
