using Microsoft.EntityFrameworkCore;
using PbxDiag.Core.Data;
using PbxDiag.Core.Models;
using System;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PbxDiag.Core.Services;

public class AIAnalysisService
{
    private readonly AppDbContext _context;

    public AIAnalysisService(AppDbContext context)
    {
        _context = context;
    }

    /// <summary>
    /// Runs an analysis on the fault logs to detect anomalies and potential root causes.
    /// </summary>
    /// <returns>A summary of the analysis findings.</returns>
    public async Task<string> AnalyzeFaultsAsync()
    {
        var recentLogs = await _context.FaultLogs
            .OrderByDescending(l => l.Timestamp)
            .Take(100) // Analyze the last 100 logs
            .ToListAsync();

        if (recentLogs.Count < 10)
        {
            return "Analysis requires at least 10 log entries. Not enough data.";
        }

        // This is a placeholder for a real ML.NET model.
        // A real implementation would involve:
        // 1. Defining an ML.NET data schema (e.g., LogData class).
        // 2. Loading the recentLogs into an IDataView.
        // 3. Using a pre-trained ML.NET model (e.g., for anomaly detection or text classification)
        //    to make predictions on the data.
        // 4. Interpreting the model's output to generate insights.

        // For now, we'll use a simple rule-based analysis as a placeholder.
        var criticalErrors = recentLogs.Count(l => l.Severity == LogSeverity.Critical);
        var warnings = recentLogs.Count(l => l.Severity == LogSeverity.Warning);

        var analysisResult = new StringBuilder();
        analysisResult.AppendLine($"Analysis complete. Scanned {recentLogs.Count} log entries.");
        analysisResult.AppendLine($"Found {criticalErrors} critical errors and {warnings} warnings.");

        if (criticalErrors > 3)
        {
            analysisResult.AppendLine("Insight: A high number of critical errors were detected recently. This may indicate a serious system failure.");
        }

        if (warnings > 10)
        {
            analysisResult.AppendLine("Insight: A high number of warnings were detected. This could be a precursor to a more significant failure. Recommend investigation.");
        }

        // Example of pattern detection
        var lowTonerWarnings = recentLogs.Count(l => l.Message.Contains("Low toner level"));
        if (lowTonerWarnings > 0)
        {
            analysisResult.AppendLine($"Insight: Detected {lowTonerWarnings} low toner alert(s). Please check network printers.");
        }

        var analysis = new AIAnalysisHistory
        {
            Timestamp = DateTime.UtcNow,
            AnalysisResult = analysisResult.ToString(),
            Summary = $"Found {criticalErrors} critical errors and {warnings} warnings.",
            RelatedLogIds = string.Join(",", recentLogs.Select(l => l.Id))
        };

        _context.AIAnalysisHistory.Add(analysis);
        await _context.SaveChangesAsync();

        return analysis.AnalysisResult;
    }
}
