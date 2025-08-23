from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseCollector(ABC):
    """
    Abstract base class for all collectors.
    It defines the common interface that all concrete collectors must implement.
    """

    def __init__(self, device: Dict[str, Any], profile: Dict[str, Any]):
        """
        Initializes the collector with device and profile information.

        :param device: A dictionary containing device details (e.g., host, credentials).
        :param profile: A dictionary containing the specific collector configuration
                        (e.g., metrics to poll, commands to run).
        """
        self.device = device
        self.profile = profile

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        The main method to perform data collection.
        This method must be implemented by all subclasses.

        :return: A dictionary containing the collected data, where keys are metric names
                 and values are the collected values. e.g., {'sysUpTime': 12345, 'cpuUsage': 15}
        """
        pass
