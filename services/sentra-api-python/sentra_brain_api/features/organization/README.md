# Organization API Usage Examples

This document demonstrates how to use the new Organization API endpoints.

## API Endpoints

### GET /organization
Retrieves the current organization configuration.

**Response (200 OK):**
```json
{
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "description": "A leading technology company",
  "location": "San Francisco, CA",
  "contact_email": "contact@acme.com"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "No organization found"
}
```

### PATCH /organization
Updates the current organization configuration.

**Request Body:**
```json
{
  "name": "Acme Corporation Inc.",
  "description": "An innovative technology company",
  "location": "San Francisco, California"
}
```

**Response (200 OK):**
```json
{
  "name": "Acme Corporation Inc.",
  "slug": "acme-corp",
  "description": "An innovative technology company", 
  "location": "San Francisco, California",
  "contact_email": "contact@acme.com"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "No organization found. Please create an organization first."
}
```

## cURL Examples

### Get Organization
```bash
curl -X GET "http://localhost:8100/organization" \
  -H "accept: application/json"
```

### Update Organization
```bash
curl -X PATCH "http://localhost:8100/organization" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Organization Name",
    "description": "Updated description"
  }'
```

## Initial Setup

Since the system assumes a single organization, you'll need to create the first organization record in the database. This can be done through the service layer:

```python
from sentra.domain.services.organization_service import OrganizationService

# Create initial organization
org_service = OrganizationService(db_session)
org_service.create_organization({
    "name": "My Organization",
    "slug": "my-org",
    "description": "Organization description",
    "location": "City, State",
    "contact_email": "admin@myorg.com"
})
```

## Database Migration

Run the Alembic migration to create the organizations table:

```bash
cd packages/sentra-core
alembic upgrade head
```

This will create the `organizations` table with the following structure:
- `id` (UUID, Primary Key)
- `name` (String, Required)
- `slug` (String, Required, Unique)
- `description` (Text, Optional)
- `location` (String, Optional) 
- `contact_email` (String, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `deleted_at` (DateTime)