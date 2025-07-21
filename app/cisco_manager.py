from pysnmp.hlapi import *

class CiscoManager:
    def __init__(self, ip_address, community_string='public'):
        self.ip_address = ip_address
        self.community_string = community_string

    def get_device_info(self):
        # OIDs for basic Cisco device information
        oids = {
            'sysName': '1.3.6.1.2.1.1.5.0',
            'sysDescr': '1.3.6.1.2.1.1.1.0',
            'sysUpTime': '1.3.6.1.2.1.1.3.0',
        }

        info = {}
        for name, oid in oids.items():
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(self.community_string),
                       UdpTransportTarget((self.ip_address, 161)),
                       ContextData(),
                       ObjectType(ObjectIdentity(oid)))
            )

            if errorIndication:
                print(errorIndication)
                info[name] = 'N/A'
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                info[name] = 'N/A'
            else:
                for varBind in varBinds:
                    info[name] = str(varBind[1])

        return info
