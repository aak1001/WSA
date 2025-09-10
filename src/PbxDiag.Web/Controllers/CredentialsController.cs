using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using PbxDiag.Core.Data;
using PbxDiag.Core.Models;
using PbxDiag.Core.Services;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace PbxDiag.Web.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CredentialsController : ControllerBase
    {
        private readonly AppDbContext _context;
        private readonly SecurityService _securityService;

        public CredentialsController(AppDbContext context, SecurityService securityService)
        {
            _context = context;
            _securityService = securityService;
        }

        // GET: api/credentials
        [HttpGet]
        public async Task<ActionResult<IEnumerable<Credential>>> GetCredentials()
        {
            // Return a list of credentials without exposing encrypted data
            var credentials = await _context.Credentials.ToListAsync();
            credentials.ForEach(c => { c.EncryptedPassword = null; c.EncryptedSshKey = null; });
            return credentials;
        }

        // GET: api/credentials/5
        [HttpGet("{id}")]
        public async Task<ActionResult<Credential>> GetCredential(int id)
        {
            var credential = await _context.Credentials.FindAsync(id);

            if (credential == null)
            {
                return NotFound();
            }

            // Do not expose encrypted data
            credential.EncryptedPassword = null;
            credential.EncryptedSshKey = null;

            return credential;
        }

        // POST: api/credentials
        [HttpPost]
        public async Task<ActionResult<Credential>> PostCredential(Credential credential)
        {
            if (!string.IsNullOrEmpty(credential.PlaintextPassword))
            {
                credential.EncryptedPassword = _securityService.Encrypt(credential.PlaintextPassword);
            }
            if (!string.IsNullOrEmpty(credential.PlaintextSshKey))
            {
                credential.EncryptedSshKey = _securityService.Encrypt(credential.PlaintextSshKey);
            }

            _context.Credentials.Add(credential);
            await _context.SaveChangesAsync();

            // Return the created object without sensitive data
            credential.EncryptedPassword = null;
            credential.PlaintextPassword = null;
            credential.EncryptedSshKey = null;
            credential.PlaintextSshKey = null;

            return CreatedAtAction(nameof(GetCredential), new { id = credential.Id }, credential);
        }

        // PUT: api/credentials/5
        [HttpPut("{id}")]
        public async Task<IActionResult> PutCredential(int id, Credential credential)
        {
            if (id != credential.Id)
            {
                return BadRequest();
            }

            var credentialToUpdate = await _context.Credentials.FindAsync(id);
            if(credentialToUpdate == null)
            {
                return NotFound();
            }

            // Update properties
            credentialToUpdate.Name = credential.Name;
            credentialToUpdate.Username = credential.Username;

            if (!string.IsNullOrEmpty(credential.PlaintextPassword))
            {
                credentialToUpdate.EncryptedPassword = _securityService.Encrypt(credential.PlaintextPassword);
            }
             if (!string.IsNullOrEmpty(credential.PlaintextSshKey))
            {
                credentialToUpdate.EncryptedSshKey = _securityService.Encrypt(credential.PlaintextSshKey);
            }

            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!CredentialExists(id))
                {
                    return NotFound();
                }
                else
                {
                    throw;
                }
            }

            return NoContent();
        }

        // DELETE: api/credentials/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteCredential(int id)
        {
            var credential = await _context.Credentials.FindAsync(id);
            if (credential == null)
            {
                return NotFound();
            }

            var isCredentialInUse = await _context.Devices.AnyAsync(d => d.CredentialId == id);
            if (isCredentialInUse)
            {
                return BadRequest("This credential is in use by one or more devices and cannot be deleted.");
            }

            _context.Credentials.Remove(credential);
            await _context.SaveChangesAsync();

            return NoContent();
        }

        private bool CredentialExists(int id)
        {
            return _context.Credentials.Any(e => e.Id == id);
        }
    }
}
