using System.Net;

namespace AlRaseel.Monitor.Core.Models;

public class Device
{
    public int Id { get; set; }
    public required string Name { get; set; }
    public required string HostnameOrIpAddress { get; set; }
    public DeviceType DeviceType { get; set; }
    public string? Model { get; set; }
    public DeviceStatus Status { get; set; }

    public int? CredentialId { get; set; }
    public Credential? Credential { get; set; }

    public ICollection<FaultLog> FaultLogs { get; set; } = new List<FaultLog>();
}
