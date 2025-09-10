using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PbxDiag.Core.Models;

public class FaultLog
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required]
    public int DeviceId { get; set; }
    [ForeignKey("DeviceId")]
    public Device Device { get; set; } = null!;

    [Required]
    public DateTime Timestamp { get; set; }

    public LogSeverity Severity { get; set; }

    [Required]
    public string Message { get; set; } = string.Empty;

    public bool Acknowledged { get; set; } = false;
}
