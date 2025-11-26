using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi;
using Scalar.AspNetCore;
using Sentra.Api.OpenApi;
using Sentra.Application.Auth;
using Sentra.Application.Users;
using Sentra.Domain.Entities;
using Sentra.Infrastructure.Auth;
using Sentra.Infrastructure.Sql;
using Sentra.Infrastructure.Sql.Repositories;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

builder.AddServiceDefaults();

builder.Services.AddProblemDetails();
builder.Services.AddControllers();

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

builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IJwtProvider, JwtProvider>();
builder.Services.AddScoped<IPasswordHasher<UserEntity>, PasswordHasher<UserEntity>>();
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddDbContext<SentraDbContext>();

// Built-in OpenAPI document generation
builder.Services.AddOpenApi(options =>
{
    // keep your existing transformer
    options.AddDocumentTransformer<BearerSecuritySchemeTransformer>();
});

// JWT setup
var jwtOptions = builder.Configuration.GetSection("JwtOptions").Get<JwtOptions>();
if (jwtOptions is null) throw new InvalidOperationException("Missing configuration section: JwtOptions");

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

var app = builder.Build();

app.UseExceptionHandler();
app.UseCors("SentraCors");

app.UseAuthentication();
app.UseAuthorization();

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
    options.SpecUrl("/openapi/v1.json"); // <- important
    options.RoutePrefix = "redoc";        // UI at /docs
    options.DocumentTitle = "Sentra API";
});

app.MapControllers();

app.MapGet("/", () => Results.Redirect("/docs"));

app.MapDefaultEndpoints();

app.Run();