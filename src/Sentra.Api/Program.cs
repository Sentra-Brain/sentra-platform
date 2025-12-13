using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Sentra.Api.Extensions;
using Sentra.Api.Features.Auth;
using Sentra.Api.Features.Users;
using Sentra.Api.OpenApi;
using Sentra.Application.Auth;
using Sentra.Application.Users;
using Sentra.Domain.Entities;
using Sentra.Infrastructure.Auth;
using Sentra.Infrastructure.Sql;
using Sentra.Infrastructure.Sql.Repositories;
using Sentra.Infrastructure.Sql.Seeding;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

builder.AddServiceDefaults();

builder.Services.AddProblemDetails();

// Add health checks
builder.Services.AddHealthChecks()
    .AddDbContextCheck<SentraDbContext>("database");

builder.Services.AddCors(options =>
{
    options.AddPolicy("SentraCors", p =>
    {
        p.WithOrigins("http://localhost:*", "https://localhost:*")
         .AllowCredentials()
         .AllowAnyHeader()
         .AllowAnyMethod();
    });
});

// Kommand CQRS configuration
builder.Services.AddKommand(config =>
{
    config.RegisterHandlersFromAssembly(typeof(Program).Assembly);
    config.WithValidation(); // Enable automatic validation
});

// Infrastructure services
builder.Services.AddScoped<IJwtProvider, JwtProvider>();
builder.Services.AddScoped<IPasswordHasher<User>, PasswordHasher<User>>();
builder.Services.AddScoped<IUserRepository, UserRepository>();



// ------------------------------------------------------------
// IMPORTANT: read Aspire-supplied connection string
// ------------------------------------------------------------
var connectionString = builder.Configuration.GetConnectionString("sentra-brain-sql");
if (string.IsNullOrWhiteSpace(connectionString))
    throw new InvalidOperationException("Aspire did not inject ConnectionStrings:sentra-brain-sql");

builder.Services.AddDbContext<SentraDbContext>(options =>
{
    options.UseNpgsql(connectionString, npg =>
    {
        npg.MigrationsAssembly("Sentra.Infrastructure");
        npg.EnableRetryOnFailure();
    });
});

// Database seeding configuration
builder.Services.AddDatabaseSeeding(builder.Configuration);

// Built-in OpenAPI document generation
builder.Services.AddOpenApi(options =>
{
    // keep your existing transformer
    options.AddDocumentTransformer<BearerSecuritySchemeTransformer>();
});

// JWT setup
var jwtOptions = builder.Configuration.GetSection("JwtOptions").Get<JwtOptions>();
if (jwtOptions is null) throw new InvalidOperationException("Missing configuration section: JwtOptions");

// Register JwtOptions for injection into JwtProvider
builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection("JwtOptions"));

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
.AddJwtBearer(o =>
{
    o.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = false,
        ValidateAudience = false,
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtOptions.Secret)),
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();

var app = builder.Build();

// Apply migrations and seed database
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<SentraDbContext>();
    db.Database.Migrate();
}

// Seed the database with initial data (admin user, etc.)
await app.SeedDatabaseAsync();

app.UseExceptionHandler();
app.UseCors("SentraCors");

app.UseAuthentication();
app.UseAuthorization();

// Map feature endpoints
app.MapAuthEndpoints();
app.MapUserEndpoints();

app.MapOpenApi();

app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/openapi/v1.json", "Sentra API v1");
    options.RoutePrefix = "docs";
    options.OAuthClientId("swagger-ui");
    options.OAuthClientSecret("swagger-ui-secret");
    options.OAuthAppName("Sentra API Explorer");
    options.OAuthUsePkce();
});

app.UseReDoc(options =>
{
    options.SpecUrl("/openapi/v1.json");
    options.RoutePrefix = "redoc";
    options.DocumentTitle = "Sentra API";
});

app.MapGet("/", () => Results.Redirect("/docs"));

app.MapDefaultEndpoints();

app.Run();