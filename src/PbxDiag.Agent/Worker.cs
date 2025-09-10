using Microsoft.EntityFrameworkCore;
using PbxDiag.Core.Data;
using PbxDiag.Core.Models;
using PbxDiag.Core.Services;

namespace PbxDiag.Agent;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly IConfiguration _configuration;
    private readonly IServiceProvider _serviceProvider;

    public Worker(ILogger<Worker> logger, IConfiguration configuration, IServiceProvider serviceProvider)
    {
        _logger = logger;
        _configuration = configuration;
        _serviceProvider = serviceProvider;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("PbxDiag Agent starting at: {time}", DateTimeOffset.Now);

        try
        {
            _logger.LogInformation("Initializing database...");
            using (var scope = _serviceProvider.CreateScope())
            {
                var dbContext = scope.ServiceProvider.GetRequiredService<AppDbContext>();
                var securityService = scope.ServiceProvider.GetRequiredService<SecurityService>();
                await dbContext.Database.MigrateAsync(stoppingToken);
                await SeedDataAsync(dbContext, securityService);
            }
            _logger.LogInformation("Database initialization complete.");
        }
        catch (Exception ex)
        {
            _logger.LogCritical(ex, "Failed to initialize the database. The agent cannot start.");
            return;
        }

        var pollingIntervalSeconds = _configuration.GetValue<int>("AgentSettings:PollingIntervalSeconds", 60);
        _logger.LogInformation("Polling interval set to {seconds} seconds.", pollingIntervalSeconds);

        while (!stoppingToken.IsCancellationRequested)
        {
            _logger.LogInformation("Worker running scan at: {time}", DateTimeOffset.Now);
            await PollDevicesAsync(stoppingToken);
            await Task.Delay(TimeSpan.FromSeconds(pollingIntervalSeconds), stoppingToken);
        }
    }

    private async Task PollDevicesAsync(CancellationToken stoppingToken)
    {
        try
        {
            using var scope = _serviceProvider.CreateScope();
            var dbContext = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            var snmpService = scope.ServiceProvider.GetRequiredService<SnmpService>();
            var sshService = scope.ServiceProvider.GetRequiredService<SshService>();
            var securityService = scope.ServiceProvider.GetRequiredService<SecurityService>();

            var devices = await dbContext.Devices.Include(d => d.Credential).ToListAsync(stoppingToken);

            if (!devices.Any())
            {
                _logger.LogWarning("No devices found in the database to poll.");
                return;
            }

            _logger.LogInformation("Found {count} devices to poll.", devices.Count);

            foreach (var device in devices)
            {
                _logger.LogInformation("--> Polling device: {name} ({type}) at {ip}", device.Name, device.DeviceType, device.IpAddress);

                switch (device.DeviceType)
                {
                    case DeviceType.NetworkPrinter:
                        var oids = await dbContext.OidMaps.Where(o => o.DeviceType == DeviceType.NetworkPrinter).ToListAsync(stoppingToken);
                        foreach (var oidMap in oids)
                        {
                            var result = await snmpService.GetAsync(device.IpAddress, device.SnmpCommunity ?? "public", oidMap.Oid);
                            _logger.LogInformation("-----> SNMP GET for {oidName} ({oid}): {result}", oidMap.Name, oidMap.Oid, result);

                            if (oidMap.Name == "TonerLevel" && int.TryParse(result, out var tonerLevel) && tonerLevel < 10)
                            {
                                var fault = new FaultLog { DeviceId = device.Id, Timestamp = DateTime.UtcNow, Severity = LogSeverity.Warning, Message = $"Low toner level detected: {tonerLevel}%" };
                                dbContext.FaultLogs.Add(fault);
                            }
                        }
                        break;

                    case DeviceType.CiscoRouter:
                        if (device.Credential?.Username != null && device.Credential?.EncryptedPassword != null)
                        {
                            var plainTextPassword = securityService.Decrypt(device.Credential.EncryptedPassword);
                            if(!string.IsNullOrEmpty(plainTextPassword))
                            {
                                var commandResult = await sshService.RunCommandAsync(device.IpAddress, device.Credential.Username, plainTextPassword, "show version");
                                _logger.LogInformation("-----> SSH 'show version' result: {result}", commandResult.Substring(0, Math.Min(commandResult.Length, 100)) + "...");
                            }
                            else
                            {
                                _logger.LogError("Failed to decrypt password for device {name}.", device.Name);
                            }
                        }
                        else
                        {
                            _logger.LogWarning("Cannot poll SSH device {name} without credentials or username.", device.Name);
                        }
                        break;

                    default:
                        _logger.LogInformation("-----> No polling logic implemented for device type: {type}", device.DeviceType);
                        break;
                }
            }
            await dbContext.SaveChangesAsync(stoppingToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "An error occurred while polling devices.");
        }
    }

    private async Task SeedDataAsync(AppDbContext context, SecurityService securityService)
    {
        if (await context.Devices.AnyAsync())
        {
            return;
        }

        _logger.LogInformation("Database is empty. Seeding with sample data...");

        var cred1 = new Credential { Name = "Default SSH", Username = "cisco", EncryptedPassword = securityService.Encrypt("cisco") };
        context.Credentials.Add(cred1);

        context.Devices.AddRange(
            new Device { Name = "Main Office Printer", IpAddress = "192.168.1.50", DeviceType = DeviceType.NetworkPrinter, SnmpCommunity = "public" },
            new Device { Name = "Core Router", IpAddress = "192.168.1.1", DeviceType = DeviceType.CiscoRouter, Credential = cred1 }
        );

        context.OidMaps.AddRange(
            new OidMap { DeviceType = DeviceType.NetworkPrinter, Oid = "1.3.6.1.2.1.1.1.0", Name = "sysDescr", Description = "System Description" },
            new OidMap { DeviceType = DeviceType.NetworkPrinter, Oid = "1.3.6.1.2.1.1.5.0", Name = "sysName", Description = "System Name" },
            new OidMap { DeviceType = DeviceType.NetworkPrinter, Oid = "1.3.6.1.2.1.43.11.1.1.9.1.1", Name = "TonerLevel", Description = "Black Toner Level Percentage" }
        );

        await context.SaveChangesAsync();
        _logger.LogInformation("Sample data seeded successfully.");
    }
}
