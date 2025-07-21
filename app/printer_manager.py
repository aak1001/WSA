from pysnmp.hlapi import *

class PrinterManager:
    def __init__(self, ip_address, community_string='public'):
        self.ip_address = ip_address
        self.community_string = community_string

    def get_printer_details(self):
        # OIDs for printer details (from RFC 3805)
        oids = {
            'model': '1.3.6.1.2.1.25.3.2.1.3.1',
            'page_count': '1.3.6.1.2.1.43.10.2.1.4.1.1',
            'toner_level': '1.3.6.1.2.1.43.11.1.1.9.1.1',
            'status': '1.3.6.1.2.1.25.3.5.1.1.1'
        }

        details = {}
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
                details[name] = 'N/A'
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                details[name] = 'N/A'
            else:
                for varBind in varBinds:
                    details[name] = str(varBind[1])

        return details
