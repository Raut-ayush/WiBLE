
<div align="center">

# 🌐 WiBLE+
### *The Future of Network Intelligence*

![License](https://img.shields.io/badge/License-MIT-00f0ff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-bc13fe?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-00e676?style=for-the-badge)

<p align="center">
  <b>WiBLE+</b> is a next-generation <b>Network Command & Control Dashboard</b> designed with a futuristic <i>Glassmorphism</i> aesthetic. 
  It combines powerful Wi-Fi scanning, rogue access point detection, and Bluetooth radar into a single, seamless interface.
</p>

---

</div>

## 🔮 Features

### 🖥️ **Glassmorphism UI**
Navigate your network in style. Our dashboard features a translucent, neon-infused interface that feels alive. Gone are the days of boring admin panels; welcome to the **Cyberpunk era** of network management.

### 📶 **Precision Network Control**
Directly manage your connections without leaving the dashboard:
- **🔌 Connect**: Securely join networks (WPA2 supported) with a sleek modal interface.
- **❌ Disconnect**: Drop connections instantly with a single click.
- **🗑️ Forget**: Remove saved profiles to ensure a clean slate.

### 🧨 **Threat Detection**
Stay one step ahead. **WiBLE+** monitors the airwaves and flags **Rogue Access Points** (APs that appear suddenly) in real-time. 
> *Secure your perimeter before they breach it.*

### ⚡ **Hyper-Speed Testing**
Integrated speed testing for:
- **⬇️ Download**
- **⬆️ Upload**
- **📡 Latency (Ping)**

### 🔵 **Bluetooth Radar**
Visualize the invisible. Our BLE Radar scans and lists nearby Bluetooth Low Energy devices, tracking their signal strength (RSSI) dynamically.

---

## 🛠️ Installation

Ensure you have **Python 3.10+** installed on Windows.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Raut-ayush/WiBLE.git
    cd WiBLE
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the System**
    ```bash
    python app.py
    ```

4.  **Access the Dashboard**
    Open your browser and navigate to:
    `http://127.0.0.1:5000`

---

## 🧑‍💻 Technologies

- **Backend**: Python (Flask)
- **Frontend**: HTML5, Modern CSS3 (Variables, Backdrop Filter), Vanilla JS
- **Scanning**:
    - `netsh` (Windows Native Wi-Fi Control)
    - `bleak` (Bluetooth Low Energy)
    - `speedtest-cli` (Ookla Speedtest)

---

<div align="center">

*Engineered for the Modern Web*
<br>
<sub>Made with 💜 by WiBLE Team</sub>

</div>
