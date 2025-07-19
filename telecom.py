import socket
from sipparty import sip
from database import log_event

def check_sip_status(ip, port=5060):
    try:
        message = sip.Message.options(
            To=f"sip:{ip}:{port}",
            From="sip:monitor@localhost"
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(message), (ip, port))
        sock.settimeout(5)
        response, addr = sock.recvfrom(1024)
        response = sip.Message.Parse(response)
        log_event("SIP status check", ip_address=ip, details=f"Status: {response.Status}")
        return response.Status
    except socket.timeout:
        log_event("SIP status check", ip_address=ip, details="No response")
        return "No response"
    except Exception as e:
        log_event("Error", ip_address=ip, details=f"An error occurred during SIP status check: {e}")
        return "Error"
    finally:
        sock.close()
