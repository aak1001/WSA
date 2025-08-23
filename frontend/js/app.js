document.addEventListener('DOMContentLoaded', () => {
    const langToggleButton = document.getElementById('lang-toggle-btn');
    const deviceStatusBody = document.getElementById('device-status-body');

    let currentLang = 'en';

    const translations = {
        en: {
            dashboard_title: 'Network Monitoring Dashboard',
            toggle_language: 'Switch to Arabic',
            device_status_title: 'Device Status',
            header_host: 'Host',
            header_status: 'Status',
            header_last_seen: 'Last Seen',
            header_details: 'Details',
            status_reachable: 'Reachable',
            status_unreachable: 'Unreachable',
        },
        ar: {
            dashboard_title: 'لوحة مراقبة الشبكة',
            toggle_language: 'التبديل إلى الإنجليزية',
            device_status_title: 'حالة الأجهزة',
            header_host: 'الجهاز',
            header_status: 'الحالة',
            header_last_seen: 'آخر ظهور',
            header_details: 'تفاصيل',
            status_reachable: 'متاح',
            status_unreachable: 'غير متاح',
        }
    };

    function setLanguage(lang) {
        currentLang = lang;
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = translations[lang][key];
        });
    }

    langToggleButton.addEventListener('click', () => {
        const newLang = currentLang === 'en' ? 'ar' : 'en';
        setLanguage(newLang);
    });

    async function fetchDeviceData() {
        try {
            const response = await fetch('/api/devices');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const devices = await response.json();
            renderDeviceTable(devices);
        } catch (error) {
            console.error("Failed to fetch device data:", error);
            deviceStatusBody.innerHTML = `<tr><td colspan="4">Error loading data. Is the backend running?</td></tr>`;
        }
    }

    function renderDeviceTable(devices) {
        if (!devices || devices.length === 0) {
            deviceStatusBody.innerHTML = `<tr><td colspan="4">No devices found.</td></tr>`;
            return;
        }

        // Clear existing rows
        deviceStatusBody.innerHTML = '';

        devices.forEach(device => {
            const row = document.createElement('tr');

            const statusText = device.is_reachable ? translations[currentLang].status_reachable : translations[currentLang].status_unreachable;
            const statusClass = device.is_reachable ? 'status-reachable' : 'status-unreachable';

            row.innerHTML = `
                <td>${device.host}</td>
                <td class="${statusClass}">${statusText}</td>
                <td>${new Date(device.last_seen).toLocaleString()}</td>
                <td><pre>${JSON.stringify(device.metrics, null, 2)}</pre></td>
            `;
            deviceStatusBody.appendChild(row);
        });
    }

    // Initial load and periodic refresh
    fetchDeviceData();
    setInterval(fetchDeviceData, 5000); // Refresh every 5 seconds

    // Set initial language
    setLanguage(currentLang);
});
