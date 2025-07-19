import socket
from sipparty import sip

class SIPMonitor:
    def __init__(self, target_ip, target_port=5060):
        self.target_ip = target_ip
        self.target_port = target_port

    def check_status(self):
        message = sip.Message.options(
            To=f"sip:{self.target_ip}:{self.target_port}",
            From="sip:monitor@localhost"
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(message), (self.target_ip, self.target_port))
        sock.settimeout(5)
        try:
            response, addr = sock.recvfrom(1024)
            response = sip.Message.Parse(response)
            return response.Status
        except socket.timeout:
            return "No response"
        finally:
            sock.close()
