using Microsoft.AspNetCore.DataProtection;
using System;

namespace PbxDiag.Core.Services
{
    public class SecurityService
    {
        private readonly IDataProtector _protector;

        // The protector is configured via DI and uses a key ring to manage keys.
        // The purpose string makes sure that keys for this usage are isolated.
        public SecurityService(IDataProtectionProvider provider)
        {
            _protector = provider.CreateProtector("PbxDiag.Credentials.v1");
        }

        public string Encrypt(string plaintext)
        {
            if (string.IsNullOrEmpty(plaintext))
            {
                return string.Empty;
            }
            return _protector.Protect(plaintext);
        }

        public string Decrypt(string ciphertext)
        {
            if (string.IsNullOrEmpty(ciphertext))
            {
                return string.Empty;
            }
            try
            {
                return _protector.Unprotect(ciphertext);
            }
            catch (Exception ex)
            {
                // Could be a problem with the key ring or malformed data.
                Console.WriteLine($"[SecurityService] Decryption failed: {ex.Message}");
                // Return empty or handle as an error, depending on security policy.
                return string.Empty;
            }
        }
    }
}
