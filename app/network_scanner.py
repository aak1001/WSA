import nmap
from scapy.all import ARP, Ether, srp

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def discover_devices(self, network):
        """
        Discovers devices on the network using ARP scan.
        """
        arp_request = ARP(pdst=network)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]

        devices = []
        for sent, received in answered_list:
            devices.append({'ip': received.psrc, 'mac': received.hwsrc})
        return devices

    def get_device_details(self, ip_address):
        """
        Gets detailed information about a device using nmap.
        """
        try:
            self.nm.scan(ip_address, '22-443')
            hostname = self.nm[ip_address].hostname()
            os_match = self.nm[ip_address].get('osmatch', [])
            os = os_match[0]['name'] if os_match else 'Unknown'
            return {'hostname': hostname, 'os': os}
        except Exception as e:
            return {'hostname': 'Unknown', 'os': 'Unknown'}
