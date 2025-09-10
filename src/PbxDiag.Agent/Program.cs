using PbxDiag.Agent;
using PbxDiag.Core.Data;
using PbxDiag.Core.Services;

var builder = Host.CreateApplicationBuilder(args);

// Register DbContext and services for dependency injection
builder.Services.AddDbContext<AppDbContext>();
builder.Services.AddScoped<SnmpService>();
builder.Services.AddScoped<SshService>();
builder.Services.AddScoped<HttpService>();
builder.Services.AddScoped<SecurityService>();

// Add ASP.NET Core Data Protection services
builder.Services.AddDataProtection();

builder.Services.AddHostedService<Worker>();

var host = builder.Build();
host.Run();
