import paramiko
import telnetlib
import subprocess

class Connection:
    def __init__(self, ip_address, username, password):
        self.ip_address = ip_address
        self.username = username
        self.password = password

    def ssh_connect(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.ip_address, username=self.username, password=self.password)
            # For now, just return the client. In a real app, you'd want to
            # open a new terminal window or provide an interactive shell.
            return client
        except Exception as e:
            print(f"SSH connection failed: {e}")
            return None

    def telnet_connect(self):
        # Telnet is insecure, use with caution.
        # This is a placeholder for a more robust implementation.
        try:
            tn = telnetlib.Telnet(self.ip_address)
            # This is a simplified example. A real implementation would need
            # to handle authentication and provide an interactive shell.
            return tn
        except Exception as e:
            print(f"Telnet connection failed: {e}")
            return None

    def rdp_connect(self):
        # This will launch the native Windows RDP client.
        try:
            subprocess.run(["mstsc", "/v:", self.ip_address])
        except FileNotFoundError:
            print("RDP client not found. Please ensure you are on Windows.")
        except Exception as e:
            print(f"RDP connection failed: {e}")
