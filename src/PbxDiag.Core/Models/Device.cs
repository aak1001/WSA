using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PbxDiag.Core.Models;

public class Device
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;

    [Required]
    [StringLength(100)]
    public string IpAddress { get; set; } = string.Empty;

    public DeviceType DeviceType { get; set; } = DeviceType.Unknown;

    public SnmpVersion SnmpVersion { get; set; } = SnmpVersion.V2c;

    [StringLength(100)]
    public string? SnmpCommunity { get; set; }

    public int? CredentialId { get; set; }
    [ForeignKey("CredentialId")]
    public Credential? Credential { get; set; }
}
