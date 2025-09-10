using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using PbxDiag.Core.Data;
using PbxDiag.Core.Models;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace PbxDiag.Web.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class LogsController : ControllerBase
    {
        private readonly AppDbContext _context;

        public LogsController(AppDbContext context)
        {
            _context = context;
        }

        // GET: api/logs
        [HttpGet]
        public async Task<ActionResult<IEnumerable<FaultLog>>> GetLogs(
            [FromQuery] int? deviceId,
            [FromQuery] LogSeverity? severity,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 50)
        {
            var query = _context.FaultLogs.AsQueryable();

            if (deviceId.HasValue)
            {
                query = query.Where(log => log.DeviceId == deviceId.Value);
            }

            if (severity.HasValue)
            {
                query = query.Where(log => log.Severity == severity.Value);
            }

            // Order by most recent first
            query = query.OrderByDescending(log => log.Timestamp);

            // Apply pagination
            var logs = await query
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .Include(log => log.Device) // Include device info
                .ToListAsync();

            return logs;
        }

        // GET: api/logs/5
        [HttpGet("{id}")]
        public async Task<ActionResult<FaultLog>> GetLog(int id)
        {
            var faultLog = await _context.FaultLogs.Include(log => log.Device)
                                                   .FirstOrDefaultAsync(log => log.Id == id);

            if (faultLog == null)
            {
                return NotFound();
            }

            return faultLog;
        }
    }
}
