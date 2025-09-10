using Microsoft.AspNetCore.Mvc;
using PbxDiag.Core.Services;
using System.Threading.Tasks;

namespace PbxDiag.Web.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AnalysisController : ControllerBase
    {
        private readonly AIAnalysisService _analysisService;

        public AnalysisController(AIAnalysisService analysisService)
        {
            _analysisService = analysisService;
        }

        // POST: api/analysis/run
        [HttpPost("run")]
        public async Task<IActionResult> RunAnalysis()
        {
            try
            {
                var result = await _analysisService.AnalyzeFaultsAsync();
                return Ok(new { AnalysisResult = result });
            }
            catch (System.Exception ex)
            {
                // In a real app, log this exception properly
                return StatusCode(500, $"An error occurred during analysis: {ex.Message}");
            }
        }
    }
}
