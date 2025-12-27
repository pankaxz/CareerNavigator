using CareerNavigator.Core.Engines;

var builder = WebApplication.CreateBuilder(args);

// Register CareerNavigator Engines
builder.Services.AddSingleton<IUniverseProvider, UniverseProvider>();
builder.Services.AddScoped<SkillScanner>();

builder.Services.AddControllers().AddNewtonsoftJson();
builder.Services.AddCors(opt => opt.AddPolicy("NavGui", p =>
    p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();

app.UseCors("NavGui");
app.MapControllers(); // This tells .NET to look at your MapController.cs

// Add a default root endpoint to prevent 404 on localhost:5128
app.MapGet("/", () => "CareerNavigator Core API is running. Access /api/map/universe to see the data.");

app.Run();