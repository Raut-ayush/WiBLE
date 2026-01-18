
// State
let networks = [];
let currentPasswordSSID = null;

// DOM Elements
const speedVal = document.getElementById('speed-val');
const speedUnit = document.getElementById('speed-unit');
const pingVal = document.getElementById('ping-val');
const uploadVal = document.getElementById('upload-val');
const wifiList = document.getElementById('wifi-list');
const rogueList = document.getElementById('rogue-list');
const bleList = document.getElementById('ble-list');
const lastScan = document.getElementById('last-scan');
const modal = document.getElementById('password-modal');
const modalTitle = document.getElementById('modal-title');
const passwordInput = document.getElementById('password-input');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    setInterval(fetchStatus, 3000); // Poll every 3 seconds
});

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateDashboard(data);
    } catch (e) {
        console.error("Failed to fetch status:", e);
    }
}

function updateDashboard(data) {
    if (data.timestamp) lastScan.textContent = `Last Scan: ${data.timestamp}`;

    // Speed
    if (data.internet && data.internet.connected) {
        speedVal.textContent = data.internet.speed.download;
        uploadVal.textContent = `${data.internet.speed.upload} Mbps`;
        pingVal.textContent = `${data.internet.speed.ping} ms`;
    } else {
        speedVal.textContent = "0";
        uploadVal.textContent = "-";
        pingVal.textContent = "-";
    }

    // Wi-Fi
    wifiList.innerHTML = '';
    if (data.wifi && data.wifi.length > 0) {
        data.wifi.forEach(([ssid, rssi]) => {
            const li = document.createElement('li');
            li.className = 'network-item';
            
            const info = document.createElement('div');
            info.className = 'network-info';
            info.innerHTML = `<span class="ssid">${ssid}</span><span class="signal">${rssi} dBm</span>`;
            
            const actions = document.createElement('div');
            actions.style.display = 'flex';
            actions.style.gap = '5px';

            const connBtn = document.createElement('button');
            connBtn.className = 'btn';
            connBtn.textContent = 'Connect';
            connBtn.onclick = () => openPasswordModal(ssid);
            
            const forgetBtn = document.createElement('button');
            forgetBtn.className = 'btn btn-disconnect';
            forgetBtn.textContent = 'Forget';
            forgetBtn.onclick = () => forgetNetwork(ssid);

            actions.appendChild(connBtn);
            // Only show Forget if we want to allow forgetting any seen net (simplified)
            // Ideally we check if it's saved, but we don't have that info yet.
            // We'll add it to all for now or maybe just a designated text.
            actions.appendChild(forgetBtn);

            li.appendChild(info);
            li.appendChild(actions);
            wifiList.appendChild(li);
        });
    } else {
        wifiList.innerHTML = '<li style="padding:10px; color: #888;">Scanning...</li>';
    }

    // Rogue APs
    rogueList.innerHTML = '';
    if (data.rogue_aps && data.rogue_aps.length > 0) {
        data.rogue_aps.forEach(ap => {
            const li = document.createElement('li');
            li.className = 'rogue-item';
            li.textContent = `⚠️ Warning: New AP Detected "${ap}"`;
            rogueList.appendChild(li);
        });
    } else {
        rogueList.innerHTML = '<li style="padding:10px; color: #00e676;">All Clean. No strange APs.</li>';
    }

    // BLE
    bleList.innerHTML = '';
    if (data.ble && data.ble.length > 0) {
        data.ble.forEach(([name, addr, rssi]) => {
            const li = document.createElement('li');
            li.style.padding = '5px 0';
            li.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            li.innerHTML = `<span style="color:var(--text-primary)">${name}</span> <span style="font-size:0.8em; color:var(--text-secondary)">(${addr}) ${rssi}dBm</span>`;
            bleList.appendChild(li);
        });
    } else {
        bleList.innerHTML = '<li style="padding:10px; color: #888;">No devices nearby</li>';
    }
}

// Actions
function openPasswordModal(ssid) {
    currentPasswordSSID = ssid;
    modalTitle.textContent = `Connect to ${ssid}`;
    passwordInput.value = '';
    modal.style.display = 'flex';
    passwordInput.focus();
}

function closeModal() {
    modal.style.display = 'none';
    currentPasswordSSID = null;
}

async function submitConnect() {
    if (!currentPasswordSSID) return;
    const password = passwordInput.value;
    closeModal();
    
    alert(`Connecting to ${currentPasswordSSID}... This may take a moment.`);
    
    try {
        const res = await fetch('/connect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ssid: currentPasswordSSID, password: password})
        });
        const result = await res.json();
        alert(result.message);
    } catch (e) {
        alert("Error connecting: " + e);
    }
}

async function disconnect() {
    if(!confirm("Disconnect from current Wi-Fi?")) return;
    try {
        const res = await fetch('/disconnect', { method: 'POST' });
        const result = await res.json();
        alert(result.message);
    } catch (e) { alert("Error: " + e); }
}

async function forgetNetwork(ssid) {
    if(!confirm(`Forget network "${ssid}"?`)) return;
    try {
        const res = await fetch('/forget', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ssid: ssid})
        });
        const result = await res.json();
        alert(result.message);
    } catch (e) { alert("Error: " + e); }
}

async function triggerRescan() {
    fetch('/rescan', { method: 'POST', headers: {'Content-Type': 'application/json'} });
}

// Events
window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
}
