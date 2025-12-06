# Database Seeding

This directory contains the database seeding infrastructure for the Sentra Brain platform.

## Overview

The database seeding system automatically creates initial data during application startup, including the initial admin user. This ensures that the platform can be accessed immediately after deployment without manual data entry.

## Features

- **Automatic Admin User Creation**: Creates an initial admin user if no users exist
- **Configurable**: Can be controlled via `appsettings.json` or environment variables
- **Idempotent**: Safe to run multiple times - only seeds when database is empty
- **Environment-Aware**: Can be enabled/disabled per environment
- **Fail-Safe**: Errors in production won't prevent application startup

## Configuration

### Via appsettings.json

```json
{
  "Seeding": {
    "Enabled": true,
    "SeedAdminUser": true,
    "InitialAdminUsername": "admin",
    "InitialAdminEmail": "admin@sentra.local",
    "InitialAdminPassword": "SecurePassword123!",
    "InitialAdminFullName": "System Administrator"
  }
}
```

### Via Environment Variables

Environment variables take precedence over `appsettings.json`:

```bash
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_EMAIL=admin@example.com
INITIAL_ADMIN_PASSWORD=SecurePassword123!
INITIAL_ADMIN_FULLNAME=John Doe
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `Enabled` | bool | `true` | Master switch for all seeding operations |
| `SeedAdminUser` | bool | `true` | Whether to seed the initial admin user |
| `InitialAdminUsername` | string | `null` | Username for the admin user |
| `InitialAdminEmail` | string | `null` | Email for the admin user |
| `InitialAdminPassword` | string | `null` | Password for the admin user |
| `InitialAdminFullName` | string | `"System Administrator"` | Display name for the admin user |

## Usage

The seeding is automatically executed during application startup in `Program.cs`:

```csharp
// Register seeding services
builder.Services.AddDatabaseSeeding(builder.Configuration);

// Execute seeding after migrations
await app.SeedDatabaseAsync();
```

## Docker / Kubernetes Deployment

When deploying via Docker or Kubernetes, set environment variables in your deployment configuration:

### Docker Compose Example

```yaml
services:
  api:
    image: sentra-api:latest
    environment:
      - INITIAL_ADMIN_USERNAME=admin
      - INITIAL_ADMIN_EMAIL=admin@company.com
      - INITIAL_ADMIN_PASSWORD=YourSecurePassword
      - INITIAL_ADMIN_FULLNAME=Platform Administrator
```

### Kubernetes Secret Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sentra-admin-credentials
type: Opaque
stringData:
  INITIAL_ADMIN_USERNAME: admin
  INITIAL_ADMIN_EMAIL: admin@company.com
  INITIAL_ADMIN_PASSWORD: YourSecurePassword
  INITIAL_ADMIN_FULLNAME: Platform Administrator
```

Then reference in your Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentra-api
spec:
  template:
    spec:
      containers:
      - name: api
        image: sentra-api:latest
        envFrom:
        - secretRef:
            name: sentra-admin-credentials
```

## Microsoft Aspire Integration

The Sentra AppHost already configures these environment variables from user secrets or environment variables:

```csharp
var initialAdminUserName = builder.Configuration["INITIAL_ADMIN_USERNAME"] ?? "admin";
var initialAdminEmail = builder.Configuration["INITIAL_ADMIN_EMAIL"] ?? "admin@sentra.local";
var initialAdminPassword = builder.Configuration["INITIAL_ADMIN_PASSWORD"] ?? "Admin@123";

pythonApi
    .WithEnvironment("INITIAL_ADMIN_USERNAME", initialAdminUserName)
    .WithEnvironment("INITIAL_ADMIN_EMAIL", initialAdminEmail)
    .WithEnvironment("INITIAL_ADMIN_PASSWORD", initialAdminPassword);
```

## Security Considerations

1. **Never commit credentials** to source control
2. **Use strong passwords** in production (minimum 12 characters, mixed case, numbers, symbols)
3. **Change default credentials** immediately after first deployment
4. **Use secrets management** in production (Azure Key Vault, AWS Secrets Manager, etc.)
5. **Rotate credentials** regularly

## Behavior

### When Database is Empty
- Checks if any users exist
- If no users found and configuration is valid, creates admin user with:
  - Username from configuration
  - Email from configuration (lowercase)
  - Hashed password
  - Roles: `Admin`, `User`
  - Status: Enabled (not disabled)
  - Timezone: UTC
  - Language: English

### When Users Already Exist
- Logs informational message
- Skips admin user creation
- Continues application startup normally

### When Configuration is Missing
- Logs warning message
- Skips admin user creation
- Continues application startup normally
- **Important**: Ensure credentials are set for first-time deployment

## Extending the Seeder

To add additional seeding operations:

1. Add a new method to `DatabaseSeeder.cs`:

```csharp
private async Task SeedDefaultOrganizationAsync(CancellationToken cancellationToken)
{
    if (!await _context.Organizations.AnyAsync(cancellationToken))
    {
        var org = new Organization
        {
            Name = "Default Organization",
            Slug = "default"
        };
        await _context.Organizations.AddAsync(org, cancellationToken);
        await _context.SaveChangesAsync(cancellationToken);
    }
}
```

2. Call it from `SeedAsync()`:

```csharp
public async Task SeedAsync(CancellationToken cancellationToken = default)
{
    await SeedAdminUserAsync(cancellationToken);
    await SeedDefaultOrganizationAsync(cancellationToken); // New seeder
}
```

3. Add configuration options to `SeedConfiguration` if needed

## Troubleshooting

### Admin user not created
- Check logs for error messages
- Verify environment variables are set correctly
- Ensure database connection is working
- Confirm migrations have been applied
- Check that `Seeding:Enabled` is `true`

### Password doesn't meet requirements
Ensure your password includes:
- At least 8 characters (12+ recommended)
- Mixed case letters
- Numbers
- Special characters

### Seeding runs every time
This shouldn't happen - seeding checks for existing users. If it does:
- Check database connection
- Verify migrations are applied correctly
- Check logs for errors during user creation

## Related Files

- `DatabaseSeeder.cs` - Main seeding implementation
- `DatabaseSeederExtensions.cs` - Extension methods for DI and startup
- `SeedConfiguration.cs` - Configuration model
- `Program.cs` - Integration point in Sentra.Api
- `appsettings.json` - Base configuration
- `appsettings.Development.json` - Development overrides
