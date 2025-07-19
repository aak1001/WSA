import scapy.all as scapy
import socket
import time
import mac_vendors
from database import log_event
import nmap

def get_devices(ip_range):
    try:
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

        devices = []
        for element in answered_list:
            hostname = get_hostname(element[1].psrc)
            ping_time = ping(element[1].psrc)
            vendor = get_mac_vendor(element[1].hwsrc)
            os = os_fingerprint(element[1].psrc)
            device = {
                "ip": element[1].psrc,
                "mac": element[1].hwsrc,
                "hostname": hostname,
                "ping": ping_time,
                "vendor": vendor,
                "os": os
            }
            devices.append(device)
        return devices
    except Exception as e:
        log_event("Error", details=f"An error occurred during device discovery: {e}")
        return []

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Unknown"

def ping(ip):
    try:
        packet = scapy.IP(dst=ip)/scapy.ICMP()
        start_time = time.time()
        response = scapy.sr1(packet, timeout=1, verbose=False)
        end_time = time.time()
        if response:
            return f"{(end_time - start_time) * 1000:.2f} ms"
        else:
            return "Timeout"
    except Exception as e:
        log_event("Error", ip_address=ip, details=f"An error occurred during ping: {e}")
        return "Error"

def get_mac_vendor(mac):
    try:
        return mac_vendors.get_vendor(mac)
    except Exception:
        return "Unknown"

def port_scan(ip, ports):
    open_ports = []
    try:
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
    except Exception as e:
        log_event("Error", ip_address=ip, details=f"An error occurred during port scan: {e}")
    return open_ports

def os_fingerprint(ip):
    try:
        nm = nmap.PortScanner()
        nm.scan(ip, arguments='-O')
        if 'osmatch' in nm[ip] and nm[ip]['osmatch']:
            return nm[ip]['osmatch'][0]['name']
        else:
            return "Unknown"
    except Exception as e:
        log_event("Error", ip_address=ip, details=f"An error occurred during OS fingerprinting: {e}")
        return "Error"
