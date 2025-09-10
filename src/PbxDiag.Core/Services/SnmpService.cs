using SnmpSharpNet;
using System;
using System.Net;
using System.Threading.Tasks;

namespace PbxDiag.Core.Services;

public class SnmpService
{
    // Default timeout for SNMP requests
    private const int DefaultTimeout = 2000; // 2 seconds

    /// <summary>
    /// Performs an SNMP GET request to retrieve a value from a single OID.
    /// </summary>
    /// <param name="ipAddress">The IP address of the target device.</param>
    /// <param name="community">The SNMP community string.</param>
    /// <param name="oid">The OID to query.</param>
    /// <returns>The value of the OID as a string, or an error message.</returns>
    public async Task<string> GetAsync(string ipAddress, string community, string oid)
    {
        try
        {
            // Using a Task.Run to avoid blocking on synchronous network I/O
            return await Task.Run(() =>
            {
                var target = new UdpTarget((IPAddress)System.Net.IPAddress.Parse(ipAddress));
                var pdu = new Pdu(PduType.Get);
                pdu.VbList.Add(oid);

                var param = new AgentParameters(new OctetString(community));
                param.Version = SnmpVersion.Ver2; // Default to v2c

                SnmpV2Packet? result = null;
                try
                {
                    result = (SnmpV2Packet)target.Request(pdu, param);
                }
                finally
                {
                    target.Close();
                }

                if (result == null)
                {
                    return "Error: No response from agent.";
                }

                if (result.Pdu.ErrorStatus != 0)
                {
                    return $"Error: SNMP error status {result.Pdu.ErrorStatus}, index {result.Pdu.ErrorIndex}";
                }

                return result.Pdu.VbList[0].Value?.ToString() ?? "Error: Null value received from agent.";
            });
        }
        catch (Exception ex)
        {
            // Log the exception details for debugging
            Console.WriteLine($"[SnmpService] Exception: {ex.Message}");
            return $"Error: {ex.Message}";
        }
    }

    // TODO: Implement SNMP WALK for retrieving tables or multiple values.
    // TODO: Implement SNMP SET for changing values on a device.
    // TODO: Add support for SNMPv3 with authentication and encryption.
}
