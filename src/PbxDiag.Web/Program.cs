using PbxDiag.Core.Data;
using PbxDiag.Core.Services;

var builder = WebApplication.CreateBuilder(args);

// --- Dependency Injection Setup ---
builder.Services.AddControllers();

// Register DbContext and services
builder.Services.AddDbContext<AppDbContext>();
builder.Services.AddScoped<SnmpService>();
builder.Services.AddScoped<SshService>();
builder.Services.AddScoped<HttpService>();
builder.Services.AddScoped<AIAnalysisService>();
builder.Services.AddScoped<SecurityService>();

// Add ASP.NET Core Data Protection services
builder.Services.AddDataProtection();

// Add Swagger/OpenAPI services
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "PbxDiag AI API", Version = "v1" });
});


var app = builder.Build();

// --- HTTP Request Pipeline Configuration ---

// Enable Swagger UI only in development
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "PbxDiag AI API v1"));
}

app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

// Map attribute-routed API controllers
app.MapControllers();

app.Run();
