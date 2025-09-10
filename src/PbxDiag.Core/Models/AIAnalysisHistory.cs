using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PbxDiag.Core.Models;

public class AIAnalysisHistory
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required]
    public DateTime Timestamp { get; set; }

    /// <summary>
    /// The detailed result of the AI analysis, potentially as a JSON string.
    /// </summary>
    [Required]
    public string AnalysisResult { get; set; } = string.Empty;

    /// <summary>
    /// A comma-separated list of FaultLog IDs that this analysis is related to.
    /// </summary>
    public string? RelatedLogIds { get; set; }

    /// <summary>
    /// A summary of the findings.
    /// </summary>
    [StringLength(500)]
    public string? Summary { get; set; }
}
