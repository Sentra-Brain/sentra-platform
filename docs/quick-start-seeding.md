# Quick Start: Database Seeding

## TL;DR

When you start the Sentra API for the first time, it will automatically create an admin user if the database is empty.

## Default Development Credentials

```
Username: admin
Email: admin@sentra.local
Password: Admin@123
```

## How to Use

### 1. First Time Setup

```bash
# Start the application via Aspire
dotnet run --project src/Sentra.AppHost

# Or just the API
dotnet run --project src/Sentra.Api
```

**Check the logs** - you should see:
```
[Information] No users found. Creating initial admin user: admin (admin@sentra.local)
[Information] ✓ Initial admin user created successfully: admin (ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
```

### 2. Login

Use the `/auth/login` endpoint:

```bash
POST http://localhost:5000/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin@123"
}
```

Or via the Swagger UI at: `http://localhost:5000/docs`

### 3. Subsequent Starts

On subsequent startups, you'll see:
```
[Information] Users already exist in the database. Skipping admin user seeding
```

The admin user is only created once.

## Customizing Credentials

### Option 1: Environment Variables (Recommended)

```bash
# PowerShell
$env:INITIAL_ADMIN_USERNAME="myadmin"
$env:INITIAL_ADMIN_EMAIL="admin@mycompany.com"
$env:INITIAL_ADMIN_PASSWORD="MySecurePassword123!"

# Bash
export INITIAL_ADMIN_USERNAME="myadmin"
export INITIAL_ADMIN_EMAIL="admin@mycompany.com"
export INITIAL_ADMIN_PASSWORD="MySecurePassword123!"
```

### Option 2: appsettings.Development.json

Edit `src/Sentra.Api/appsettings.Development.json`:

```json
{
  "Seeding": {
    "InitialAdminUsername": "myadmin",
    "InitialAdminEmail": "admin@mycompany.com",
    "InitialAdminPassword": "MySecurePassword123!"
  }
}
```

⚠️ **Never commit real passwords to Git!**

### Option 3: User Secrets (Best for Development)

```bash
cd src/Sentra.Api

dotnet user-secrets set "Seeding:InitialAdminUsername" "myadmin"
dotnet user-secrets set "Seeding:InitialAdminEmail" "admin@mycompany.com"
dotnet user-secrets set "Seeding:InitialAdminPassword" "MySecurePassword123!"
```

## Disabling Seeding

If you want to disable automatic seeding:

```json
{
  "Seeding": {
    "Enabled": false
  }
}
```

Or just disable admin user creation:

```json
{
  "Seeding": {
    "SeedAdminUser": false
  }
}
```

## Resetting and Re-seeding

To test seeding again:

### Option 1: Delete All Users (Soft)

```sql
DELETE FROM users;
```

Then restart the API.

### Option 2: Drop Database (Hard)

```bash
# Stop the API
# Then drop the database
docker exec -it sentra-postgres psql -U postgres -c "DROP DATABASE \"sentra-brain-sql\";"
docker exec -it sentra-postgres psql -U postgres -c "CREATE DATABASE \"sentra-brain-sql\";"

# Restart the API - migrations and seeding will run automatically
```

## Troubleshooting

### Problem: "No users found" but no admin created

**Check logs for:**
- ⚠️ "Cannot seed admin user: missing required configuration"

**Solution:** Set all required environment variables or appsettings values.

### Problem: Wrong password

**Solution:** 
1. Delete the user from database
2. Update configuration with correct password
3. Restart API

### Problem: Seeding runs every time

**This shouldn't happen!** If it does:
1. Check database connection
2. Verify users table exists
3. Check for errors in logs during user creation

## Production Deployment

For production, **always** use environment variables or secrets management:

### Docker Compose

```yaml
services:
  api:
    environment:
      - INITIAL_ADMIN_USERNAME=${ADMIN_USERNAME}
      - INITIAL_ADMIN_EMAIL=${ADMIN_EMAIL}
      - INITIAL_ADMIN_PASSWORD=${ADMIN_PASSWORD}
```

### Kubernetes

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sentra-admin-creds
type: Opaque
stringData:
  INITIAL_ADMIN_USERNAME: admin
  INITIAL_ADMIN_EMAIL: admin@company.com
  INITIAL_ADMIN_PASSWORD: VerySecurePassword123!
```

### Azure App Service

```bash
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name mySentraApp \
  --settings \
    INITIAL_ADMIN_USERNAME="admin" \
    INITIAL_ADMIN_EMAIL="admin@company.com" \
    INITIAL_ADMIN_PASSWORD="SecurePassword123!"
```

## Security Checklist

✅ Use strong passwords (12+ characters)  
✅ Change default password after first login  
✅ Never commit credentials to Git  
✅ Use environment variables in production  
✅ Rotate credentials regularly  
✅ Use secrets management (Azure Key Vault, AWS Secrets Manager)  

## See Also

- Full documentation: `src/Sentra.Infrastructure/Sql/Seeding/README.md`
- Implementation details: `docs/database-seeding-implementation.md`
- Architecture guide: `.github/copilot-instructions.md`
