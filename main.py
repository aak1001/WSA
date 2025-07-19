from fastapi import FastAPI
from scanner import Scanner
from logger import log_event
from intelligence import check_for_new_devices

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "LAN Monitor API"}

@app.get("/discover")
async def discover_devices(ip_range: str = "192.168.1.1/24"):
    scanner = Scanner(ip_range)
    devices = scanner.scan()
    log_event(f"Discovered {len(devices)} devices on {ip_range}")
    for device in devices:
        log_event(f"Device found: {device['ip']} ({device['mac']}) - {device['vendor']}")

    new_devices = check_for_new_devices(devices)
    if new_devices:
        log_event(f"ALERT: Found {len(new_devices)} new devices:")
        for device in new_devices:
            log_event(f"  - New device: {device['ip']} ({device['mac']}) - {device['vendor']}")

    return {"devices": devices, "new_devices": new_devices}

@app.get("/scan_ports/{ip_address}")
async def scan_ports(ip_address: str, ports: str = "1-1024"):
    scanner = Scanner(ip_address)
    port_list = []
    if "-" in ports:
        start, end = ports.split("-")
        port_list = range(int(start), int(end) + 1)
    else:
        port_list = [int(p) for p in ports.split(",")]

    open_ports = scanner.port_scan(ip_address, port_list)
    return {"ip_address": ip_address, "open_ports": open_ports}

from telecom import SIPMonitor

@app.get("/snmp_scan/{ip_address}")
async def snmp_scan(ip_address: str, oid: str = "1.3.6.1.2.1.1.1.0"):
    scanner = Scanner(ip_address)
    result = scanner.snmp_scan(ip_address, oid)
    return {"ip_address": ip_address, "oid": oid, "result": result}

@app.get("/check_sip/{ip_address}")
async def check_sip_status(ip_address: str, port: int = 5060):
    monitor = SIPMonitor(ip_address, port)
    status = monitor.check_status()
    return {"ip_address": ip_address, "port": port, "status": status}
