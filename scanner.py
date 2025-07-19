import scapy.all as scapy
import mac_vendors
import socket
from pysnmp.hlapi import *

class Scanner:
    def __init__(self, ip_range):
        self.ip_range = ip_range
        self.devices = []

    def scan(self):
        arp_request = scapy.ARP(pdst=self.ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

        for element in answered_list:
            device_info = {
                "ip": element[1].psrc,
                "mac": element[1].hwsrc,
                "vendor": self.get_mac_vendor(element[1].hwsrc),
                "hostname": self.get_hostname(element[1].psrc)
            }
            self.devices.append(device_info)

        return self.devices

    def get_hostname(self, ip_address):
        try:
            return socket.gethostbyaddr(ip_address)[0]
        except socket.herror:
            return "Unknown"

    def get_mac_vendor(self, mac_address):
        try:
            return mac_vendors.get_vendor(mac_address)
        except Exception:
            return "Unknown"

    def port_scan(self, ip_address, ports):
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip_address, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except socket.error:
                pass
        return open_ports

    def snmp_scan(self, ip_address, oid):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData('public', mpModel=0),
                   UdpTransportTarget((ip_address, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if errorIndication:
            return str(errorIndication)
        elif errorStatus:
            return '%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            for varBind in varBinds:
                return ' = '.join([x.prettyPrint() for x in varBind])
