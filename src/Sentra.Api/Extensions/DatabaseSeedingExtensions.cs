using Microsoft.Extensions.Logging;
using Sentra.Infrastructure.Sql.Seeding;

namespace Sentra.Api.Extensions;

/// <summary>
/// Extension methods for database seeding during application startup.
/// </summary>
public static class DatabaseSeedingExtensions
{
    /// <summary>
    /// Executes database seeding during application startup.
    /// </summary>
    /// <param name="app">The web application instance.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The web application for chaining.</returns>
    public static async Task<WebApplication> SeedDatabaseAsync(
        this WebApplication app,
        CancellationToken cancellationToken = default)
    {
        using var scope = app.Services.CreateScope();
        var seeder = scope.ServiceProvider.GetRequiredService<DatabaseSeeder>();
        
        try
        {
            await seeder.SeedAsync(cancellationToken);
        }
        catch (Exception ex)
        {
            var logger = scope.ServiceProvider.GetRequiredService<ILogger<DatabaseSeeder>>();
            logger.LogError(ex, "An error occurred while seeding the database");
            
            // Re-throw in development, but continue in production to prevent startup failures
            if (app.Environment.IsDevelopment())
            {
                throw;
            }
        }

        return app;
    }

    /// <summary>
    /// Executes database seeding during application startup (synchronous version).
    /// </summary>
    /// <param name="app">The web application instance.</param>
    /// <returns>The web application for chaining.</returns>
    public static WebApplication SeedDatabase(this WebApplication app)
    {
        using var scope = app.Services.CreateScope();
        var seeder = scope.ServiceProvider.GetRequiredService<DatabaseSeeder>();
        
        try
        {
            seeder.SeedAsync().GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            var logger = scope.ServiceProvider.GetRequiredService<ILogger<DatabaseSeeder>>();
            logger.LogError(ex, "An error occurred while seeding the database");
            
            // Re-throw in development, but continue in production to prevent startup failures
            if (app.Environment.IsDevelopment())
            {
                throw;
            }
        }

        return app;
    }
}
