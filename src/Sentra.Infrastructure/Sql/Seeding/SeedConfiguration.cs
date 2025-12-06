namespace Sentra.Infrastructure.Sql.Seeding;

/// <summary>
/// Configuration for database seeding operations.
/// </summary>
public sealed class SeedConfiguration
{
    /// <summary>
    /// Gets or sets whether database seeding is enabled.
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Gets or sets whether the initial admin user should be seeded.
    /// </summary>
    public bool SeedAdminUser { get; set; } = true;

    /// <summary>
    /// Gets or sets the initial admin username.
    /// </summary>
    public string? InitialAdminUsername { get; set; }

    /// <summary>
    /// Gets or sets the initial admin email.
    /// </summary>
    public string? InitialAdminEmail { get; set; }

    /// <summary>
    /// Gets or sets the initial admin password.
    /// </summary>
    public string? InitialAdminPassword { get; set; }

    /// <summary>
    /// Gets or sets the initial admin full name (optional).
    /// </summary>
    public string? InitialAdminFullName { get; set; }
}
