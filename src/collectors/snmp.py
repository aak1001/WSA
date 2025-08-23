from typing import Any, Dict
from .base import BaseCollector
import time

class SnmpCollector(BaseCollector):
    """
    A DUMMY collector for debugging purposes. It does not perform real SNMP calls.
    It returns hardcoded data to test the application framework.
    """

    def collect(self) -> Dict[str, Any]:
        """
        Returns dummy data instead of performing a real collection.
        """
        host = self.device.get("host")
        command = self.profile.get("command", "get")

        print(f"Executing DUMMY SnmpCollector for host {host} with command '{command}'")

        if command == "get":
            return {
                "sysUpTime": int(time.time()),
                "sysName": "dummy-device-name"
            }
        elif command == "walk":
            profile_name = self.profile.get("name", "walk_results")
            return {
                profile_name: [
                    {"instance": "1", "componentName": "Fan Tray 1", "componentOpStatus": "ok"},
                    {"instance": "2", "componentName": "Power Supply 2", "componentOpStatus": "failed"},
                ]
            }

        return {"dummy_error": "Unknown command"}
