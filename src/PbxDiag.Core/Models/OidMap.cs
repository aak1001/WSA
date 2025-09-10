using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PbxDiag.Core.Models;

/// <summary>
/// Maps a specific SNMP OID to a human-readable name for a given device type.
/// </summary>
public class OidMap
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    /// <summary>
    /// The type of device this OID applies to.
    /// </summary>
    [Required]
    public DeviceType DeviceType { get; set; }

    /// <summary>
    /// The numeric SNMP Object ID.
    /// </summary>
    [Required]
    [StringLength(255)]
    public string Oid { get; set; } = string.Empty;

    /// <summary>
    /// The human-readable name for this OID (e.g., "Uptime", "TonerLevel").
    /// </summary>
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// An optional description of what this OID represents.
    /// </summary>
    public string? Description { get; set; }
}
