namespace AlRaseel.Monitor.Core.Models;

public class Credential
{
    public int Id { get; set; }
    public required string Name { get; set; }
    public string? Username { get; set; }
    public string? Password { get; set; } // Will be encrypted
    public string? SnmpCommunity { get; set; }
    public string? SnmpAuthPassword { get; set; }
    public string? SnmpPrivacyPassword { get; set; }
    public byte[]? SshKey { get; set; } // For SSH key auth
}
