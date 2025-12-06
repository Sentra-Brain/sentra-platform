using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Sentra.Infrastructure.Sql.Seeding;

/// <summary>
/// Extension methods for configuring database seeding.
/// </summary>
public static class DatabaseSeederExtensions
{
    /// <summary>
    /// Adds database seeding services to the dependency injection container.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <param name="configuration">The configuration instance.</param>
    /// <returns>The service collection for chaining.</returns>
    public static IServiceCollection AddDatabaseSeeding(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // Register seed configuration
        var seedConfig = new SeedConfiguration
        {
            Enabled = configuration["Seeding:Enabled"] != "false", // true by default
            SeedAdminUser = configuration["Seeding:SeedAdminUser"] != "false", // true by default
            InitialAdminUsername = configuration["Seeding:InitialAdminUsername"]
                ?? Environment.GetEnvironmentVariable("INITIAL_ADMIN_USERNAME"),
            InitialAdminEmail = configuration["Seeding:InitialAdminEmail"]
                ?? Environment.GetEnvironmentVariable("INITIAL_ADMIN_EMAIL"),
            InitialAdminPassword = configuration["Seeding:InitialAdminPassword"]
                ?? Environment.GetEnvironmentVariable("INITIAL_ADMIN_PASSWORD"),
            InitialAdminFullName = configuration["Seeding:InitialAdminFullName"]
                ?? Environment.GetEnvironmentVariable("INITIAL_ADMIN_FULLNAME")
        };

        services.AddSingleton(seedConfig);
        services.AddScoped<DatabaseSeeder>();

        return services;
    }
}
