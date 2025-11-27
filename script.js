// Initialize the map
const map = L.map('map').setView([31.9539, 35.9106], 7); // Centered on Amman, Jordan

// Add the tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Dummy data for devices
const devices = [
    { id: 1, name: 'Amman-Server-1', ip: '192.168.1.10', status: 'online', location: [31.9539, 35.9106] },
    { id: 2, name: 'Irbid-Router-1', ip: '192.168.1.20', status: 'online', location: [32.5568, 35.8469] },
    { id: 3, name: 'Aqaba-PC-1', ip: '192.168.1.30', status: 'offline', location: [29.5269, 35.0078] },
    { id: 4, name: 'Zarqa-Switch-1', ip: '192.168.1.40', status: 'online', location: [32.0694, 36.0925] },
    { id: 5, name: 'Karak-Camera-1', ip: '192.168.1.50', status: 'offline', location: [31.1813, 35.7505] }
];

// Get the device list element
const deviceList = document.getElementById('device-list');

// Loop through the devices and display them
devices.forEach(device => {
    // Add device to the list
    const listItem = document.createElement('li');
    listItem.innerHTML = `
        <strong>${device.name}</strong> (${device.ip})
        <span class="status ${device.status}">${device.status}</span>
    `;
    deviceList.appendChild(listItem);

    // Add marker to the map
    const markerIcon = L.icon({
        iconUrl: `https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-${device.status === 'online' ? 'green' : 'red'}.png`,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    const marker = L.marker(device.location, { icon: markerIcon }).addTo(map);
    marker.bindPopup(`<strong>${device.name}</strong><br>IP: ${device.ip}<br>Status: ${device.status}`);
});

// Perform network analysis
const networkAnalysis = document.getElementById('network-analysis');
const onlineDevices = devices.filter(device => device.status === 'online').length;
const offlineDevices = devices.length - onlineDevices;

networkAnalysis.innerHTML = `
    <p>Total Devices: ${devices.length}</p>
    <p>Online: ${onlineDevices}</p>
    <p>Offline: ${offlineDevices}</p>
`;
