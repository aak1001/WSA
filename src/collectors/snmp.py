from typing import Any, Dict, List
from pysnmp.hlapi import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, getCmd, nextCmd
)
from .base import BaseCollector

class SnmpCollector(BaseCollector):
    """
    A collector for fetching data using SNMP, supporting GET and WALK commands.
    """

    def collect(self) -> Dict[str, Any]:
        """
        Delegates collection to the appropriate method based on the command
        specified in the profile ('get' or 'walk').
        """
        command = self.profile.get("command", "get").lower()

        if command == "get":
            return self._collect_get()
        elif command == "walk":
            return self._collect_walk()
        else:
            return {"snmp_error": f"Unsupported SNMP command: {command}"}

    def _collect_get(self) -> Dict[str, Any]:
        """
        Performs an SNMP GET operation for a list of OIDs.
        """
        host = self.device.get("host")
        snmp_config = self.device.get("snmp", {})
        port = snmp_config.get("port", 161)
        community = snmp_config.get("community", "public")
        metrics: List[Dict[str, str]] = self.profile.get("metrics", [])

        object_types = [ObjectType(ObjectIdentity(m['oid'])) for m in metrics]
        if not object_types:
            return {"snmp_error": "No valid OIDs found in profile for GET."}

        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),
            UdpTransportTarget((host, port), timeout=2.0, retries=3),
            ContextData(),
            *object_types
        )

        collected_data = {}
        error_indication, error_status, error_index, var_binds = next(iterator)

        if error_indication:
            collected_data['snmp_error'] = str(error_indication)
        elif error_status:
            error_msg = f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}"
            collected_data['snmp_error'] = error_msg
        else:
            for i, var_bind in enumerate(var_binds):
                metric_name = metrics[i]['name']
                collected_data[metric_name] = var_bind[1].prettyPrint()
        return collected_data

    def _collect_walk(self) -> Dict[str, Any]:
        """
        Performs an SNMP WALK operation over one or more OID subtrees.
        Formats the result as a table.
        """
        host = self.device.get("host")
        snmp_config = self.device.get("snmp", {})
        port = snmp_config.get("port", 161)
        community = snmp_config.get("community", "public")
        metrics: List[Dict[str, str]] = self.profile.get("metrics", [])

        object_types = [ObjectType(ObjectIdentity(m['oid'])) for m in metrics]
        if not object_types:
            return {"snmp_error": "No valid OIDs found in profile for WALK."}

        results_table = {}

        iterator = nextCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),
            UdpTransportTarget((host, port), timeout=5.0, retries=2), # Longer timeout for walks
            ContextData(),
            *object_types,
            lexicographicMode=False # Important for walking multiple OIDs
        )

        for error_indication, error_status, error_index, var_binds in iterator:
            if error_indication:
                return {'snmp_error': str(error_indication)}
            elif error_status:
                error_msg = f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}"
                return {'snmp_error': error_msg}
            else:
                for var_bind in var_binds:
                    oid, value = var_bind
                    oid_str = str(oid)
                    # Find which metric this OID belongs to
                    for i, metric in enumerate(metrics):
                        if oid_str.startswith(metric['oid']):
                            # The instance is the part of the OID after the base
                            instance = oid_str.replace(metric['oid'], '').lstrip('.')
                            if instance not in results_table:
                                results_table[instance] = {}
                            results_table[instance][metric['name']] = value.prettyPrint()
                            break

        # Convert the dictionary of dictionaries to a list of dictionaries
        final_results = [
            {'instance': key, **value} for key, value in results_table.items()
        ]

        # The result of a walk is a dictionary containing a single key (the profile name)
        # and the list of results as its value. This helps distinguish it in the DB.
        profile_name = self.profile.get("name", "walk_results")
        return {profile_name: final_results}
