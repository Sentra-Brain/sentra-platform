using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Sentra.Domain.Entities;
using Sentra.Domain.Enums;

namespace Sentra.Infrastructure.Sql.Seeding;

/// <summary>
/// Handles database seeding operations, including initial admin user creation.
/// </summary>
public sealed class DatabaseSeeder
{
    private readonly SentraDbContext _context;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly ILogger<DatabaseSeeder> _logger;
    private readonly SeedConfiguration _configuration;

    public DatabaseSeeder(
        SentraDbContext context,
        IPasswordHasher<User> passwordHasher,
        ILogger<DatabaseSeeder> logger,
        SeedConfiguration configuration)
    {
        _context = context;
        _passwordHasher = passwordHasher;
        _logger = logger;
        _configuration = configuration;
    }

    /// <summary>
    /// Seeds the database with initial data if needed.
    /// </summary>
    public async Task SeedAsync(CancellationToken cancellationToken = default)
    {
        if (!_configuration.Enabled)
        {
            _logger.LogInformation("Database seeding is disabled");
            return;
        }

        _logger.LogInformation("Starting database seeding...");

        await SeedAdminUserAsync(cancellationToken);

        _logger.LogInformation("Database seeding completed successfully");
    }

    /// <summary>
    /// Seeds the initial admin user if no users exist in the database.
    /// </summary>
    private async Task SeedAdminUserAsync(CancellationToken cancellationToken)
    {
        if (!_configuration.SeedAdminUser)
        {
            _logger.LogDebug("Admin user seeding is disabled");
            return;
        }

        // Check if any users exist
        var userExists = await _context.Users.AnyAsync(cancellationToken);
        if (userExists)
        {
            _logger.LogInformation("Users already exist in the database. Skipping admin user seeding");
            return;
        }

        // Validate configuration
        if (string.IsNullOrWhiteSpace(_configuration.InitialAdminUsername) ||
            string.IsNullOrWhiteSpace(_configuration.InitialAdminEmail) ||
            string.IsNullOrWhiteSpace(_configuration.InitialAdminPassword))
        {
            _logger.LogWarning(
                "Cannot seed admin user: missing required configuration. " +
                "Please set INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_EMAIL, and INITIAL_ADMIN_PASSWORD");
            return;
        }

        _logger.LogInformation(
            "No users found. Creating initial admin user: {Username} ({Email})",
            _configuration.InitialAdminUsername,
            _configuration.InitialAdminEmail);

        var adminUser = new User
        {
            Id = Guid.NewGuid(),
            Username = _configuration.InitialAdminUsername,
            Email = _configuration.InitialAdminEmail.ToLowerInvariant(),
            FullName = _configuration.InitialAdminFullName ?? "System Administrator",
            Disabled = false, // Admin is enabled by default
            PreferredLanguage = "en",
            Timezone = "UTC",
            CreatedAt = DateTime.UtcNow
        };

        // Hash the password
        adminUser.HashedPassword = _passwordHasher.HashPassword(adminUser, _configuration.InitialAdminPassword);

        // Set admin and user roles
        adminUser.SetRoles([Role.Admin, Role.User]);

        await _context.Users.AddAsync(adminUser, cancellationToken);
        await _context.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "✓ Initial admin user created successfully: {Username} (ID: {UserId})",
            adminUser.Username,
            adminUser.Id);
    }
}
