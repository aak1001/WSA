using AlRaseel.Monitor.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace AlRaseel.Monitor.Data;

public class AppDbContext : DbContext
{
    public DbSet<Device> Devices { get; set; }
    public DbSet<Credential> Credentials { get; set; }
    public DbSet<FaultLog> FaultLogs { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        // For simplicity, we're putting the connection string here.
        // In a real app, this would come from configuration.
        optionsBuilder.UseSqlite("Data Source=alraseel_monitor.db");
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure relationships and constraints if needed
        modelBuilder.Entity<Device>()
            .HasMany(d => d.FaultLogs)
            .WithOne(f => f.Device)
            .HasForeignKey(f => f.DeviceId);

        modelBuilder.Entity<Device>()
            .HasOne(d => d.Credential)
            .WithMany() // A credential could potentially be used by multiple devices in the future
            .HasForeignKey(d => d.CredentialId);
    }
}
