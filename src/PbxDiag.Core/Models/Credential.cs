using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PbxDiag.Core.Models;

public class Credential
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;

    [StringLength(100)]
    public string? Username { get; set; }

    /// <summary>
    /// Stores the encrypted password. This is what's saved in the database.
    /// </summary>
    public string? EncryptedPassword { get; set; }

    /// <summary>
    /// Used only for receiving a new password from the user.
    /// It will be encrypted and stored in EncryptedPassword.
    /// It will NOT be stored in the database.
    /// </summary>
    [NotMapped]
    public string? PlaintextPassword { get; set; }

    /// <summary>
    /// Stores the encrypted private key for SSH.
    /// </summary>
    public string? EncryptedSshKey { get; set; }

    /// <summary>
    /// Used for receiving a new SSH key from the user.
    /// </summary>
    [NotMapped]
    public string? PlaintextSshKey { get; set; }
}
