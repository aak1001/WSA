namespace AlRaseel.Monitor.Core.Models;

public class FaultLog
{
    public long Id { get; set; }
    public int DeviceId { get; set; }
    public Device Device { get; set; } = null!;
    public DateTime Timestamp { get; set; }
    public FaultSeverity Severity { get; set; }
    public required string Message { get; set; }
    public bool Acknowledged { get; set; } = false;
}
