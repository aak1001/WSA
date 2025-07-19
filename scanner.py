import scapy.all as scapy
import socket
import time
import mac_vendors

def get_devices(ip_range):
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    devices = []
    for element in answered_list:
        hostname = get_hostname(element[1].psrc)
        ping_time = ping(element[1].psrc)
        vendor = get_mac_vendor(element[1].hwsrc)
        device = {
            "ip": element[1].psrc,
            "mac": element[1].hwsrc,
            "hostname": hostname,
            "ping": ping_time,
            "vendor": vendor
        }
        devices.append(device)
    return devices

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
    except Exception:
        return "Error"

def get_mac_vendor(mac):
    try:
        return mac_vendors.get_vendor(mac)
    except Exception:
        return "Unknown"

def port_scan(ip, ports):
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports
