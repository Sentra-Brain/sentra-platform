# GitHub Copilot Instructions for Sentra Brain Platform

## Project Context

Hybrid C#/.NET + Python on-premises AI platform prioritizing privacy, compliance (GDPR/HIPAA/ISO27001), and modularity.

**Tech Stack:** C# (.NET 10), Python (RAG only), Microsoft Aspire, MongoDB, PostgreSQL, Chroma, RabbitMQ

## Architecture

### Core Principles
- **C# (.NET 10)**: API, business logic, domain models, infrastructure
- **Python**: RAG services only (vector search, embeddings, document ingestion)
- **Microsoft Aspire**: Service orchestration, observability, configuration (`src/Sentra.AppHost`)
- **Vertical Slice Architecture**: Features organized by business capability
- **CQRS**: Commands (writes) and Queries (reads) separated via **Kommand** mediator library

### Project Structure
```
src/
├── Sentra.Api/            # Controller-based API (NOT minimal APIs)
├── Sentra.AppHost/        # Aspire orchestration
├── Sentra.Domain/         # Domain entities, value objects
├── Sentra.Application/    # Use cases, CQRS handlers
├── Sentra.Infrastructure/ # EF Core, repositories, external integrations
├── Sentra.Contracts/      # DTOs, API contracts
├── Sentra.Rag.Server/     # Python: RAG vector search
└── Sentra.Rag.Worker/     # Python: Document ingestion
```

**Legacy (reference only):**
- `src/Sentra.Api.Python` - Being migrated to C#
- `packages/sentra-domain`, `packages/sentra-infra` - Legacy Python

## Development Patterns

### C# API (Controller-Based)
- **Use Controllers** (NOT minimal APIs)
- **CQRS via Kommand**: `ICommand<TResponse>`, `IQuery<TResponse>`
- **Vertical Slices**: Organize by feature (e.g., `Features/Users/`, `Features/Organizations/`)
- **Handlers**: `ICommandHandler<TCommand, TResponse>`, `IQueryHandler<TQuery, TResponse>`
- **Validation**: `IValidator<TRequest>` with async database checks
- **Interceptors**: Type-specific (command-only, query-only, or both)
- **DI**: Scoped handlers for DbContext integration
- **Result Pattern**: Return `Result<T>` instead of throwing exceptions for business failures
- **API Models**: Use dedicated Request/Response models (e.g., `CreateUserRequest`, `UserResponse`) from `Sentra.Contracts`, never expose domain entities
- **Domain Entities**: No suffixes - `User`, `Organization` (not `UserEntity`, `OrganizationEntity`)

### Python (RAG Services Only)
- FastAPI for endpoints
- Async patterns, Pydantic validation
- **Do NOT** add business logic outside RAG domain

## Best Practices

### Code Quality
- **Async/await** for all I/O
- **Record types** for DTOs
- **XML comments** on public APIs
- **PascalCase** (C# public), **camelCase** (C# private), **snake_case** (Python)

### Testing
- **xUnit** (C#): Unit + integration tests (WebApplicationFactory)
- **pytest** (Python): Mock external services
- **>80% coverage** on business logic

### Observability
- OpenTelemetry integrated via Kommand and Aspire
- Aspire dashboard: `http://localhost:15888`

### Security
- No external telemetry
- JWT authentication, role-based authorization
- Secrets in user-secrets (dev) or Azure Key Vault (prod)
- Never commit credentials

## Workflow

### Adding Features (C#)
1. Define command/query in `Features/<Domain>/<Action>.cs`
2. Implement handler (business logic)
3. Add validator if needed
4. Create controller endpoint
5. Write tests
6. Register in DI (auto-discovered by Kommand)

### Running Locally
- Infrastructure: `cd deploy && docker compose -f docker-compose.dev.yml up -d`
- All services via Aspire: `dotnet run --project src/Sentra.AppHost`

### Database
- **MongoDB**: User data, sessions
- **PostgreSQL**: Structured data (EF Core migrations: `dotnet ef migrations add <Name>`)
- **Chroma**: Vectors (Python only)

## CI/CD & Commits

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat(scope):`, `fix(scope):`, `docs(scope):`, `test(scope):`, `refactor(scope):`

### CI/CD
- All tests must pass
- Code analysis (C#: .NET analyzers, Python: mypy/pyright)
- Build before merge
- Document breaking changes

## Anti-Patterns
❌ Minimal APIs (use controllers)
❌ Business logic in Python (except RAG)
❌ Domain entities in API responses (use Request/Response models from `Sentra.Contracts`)
❌ Entity suffix on domain entities (User, not UserEntity)
❌ Hardcoded secrets/URLs
❌ Skipping tests
❌ External telemetry

## Quick Reference
| Command | Purpose |
|---------|---------|
| `dotnet run --project src/Sentra.AppHost` | Run all services |
| `dotnet test src/Sentra.Tests` | Run C# tests |
| `dotnet ef migrations add <Name> --project src/Sentra.Infrastructure` | Create migration |
| `pytest packages/sentra-rag/tests` | Run Python tests |
