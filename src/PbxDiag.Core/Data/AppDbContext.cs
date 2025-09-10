using Microsoft.EntityFrameworkCore;
using PbxDiag.Core.Models;
using System;
using System.IO;

namespace PbxDiag.Core.Data;

public class AppDbContext : DbContext
{
    public DbSet<Device> Devices { get; set; }
    public DbSet<Credential> Credentials { get; set; }
    public DbSet<FaultLog> FaultLogs { get; set; }
    public DbSet<OidMap> OidMaps { get; set; }
    public DbSet<AIAnalysisHistory> AIAnalysisHistory { get; set; }

    public string DbPath { get; }

    public AppDbContext()
    {
        // Define a path for the database in a local application folder
        var folder = Environment.SpecialFolder.LocalApplicationData;
        var path = Environment.GetFolderPath(folder);
        DbPath = Path.Join(path, "PbxDiagAI", "pbxaidiag.db");

        // Ensure the directory exists
        var dbDir = Path.GetDirectoryName(DbPath);
        if (dbDir != null && !Directory.Exists(dbDir))
        {
            Directory.CreateDirectory(dbDir);
        }
    }

    // The following configures EF to create a Sqlite database file in the
    // special "local" folder for your platform.
    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseSqlite($"Data Source={DbPath}");
}
