# Sentra Brain – Agent Coding Guide (2025)

## Overview

Sentra Brain is a modular, private AI server platform for professional environments needing compliance, privacy, and control. The platform is built as a monorepo with a hybrid architecture: **C# (.NET) for API and business logic**, and **Python for RAG (Retrieval Augmented Generation) services**.

All code, data, and computation are designed to remain on-premises. The system is built for extensibility, regulatory compliance (GDPR, HIPAA, ISO/IEC 27001), and modularity.

## Architecture Philosophy

- **C# (.NET 10)**: Main API, business logic, domain models, and infrastructure orchestrated via **Microsoft Aspire**
- **Python**: Independent RAG microservices (vector search, document ingestion, embeddings)
- **Microsoft Aspire**: Service orchestration, configuration, and observability (see `src/Sentra.AppHost`)
- **Docker Compose**: Deployment and infrastructure services (databases, message queues, monitoring)

## Monorepo Structure

| Path                        | Purpose                                                                                 |
|-----------------------------|-----------------------------------------------------------------------------------------|
| `src/Sentra.sln`            | Main .NET solution containing all C# projects.                                           |
| `src/Sentra.Api`            | Main REST API gateway (C#), orchestrates business logic, integrates with databases.      |
| `src/Sentra.AppHost`        | **Microsoft Aspire orchestration** – service discovery, config, and observability.       |
| `src/Sentra.Domain`         | Core domain logic, entities, and business rules (C#).                                    |
| `src/Sentra.Application`    | Application services, use cases, and orchestration (C#).                                 |
| `src/Sentra.Infrastructure` | Data persistence, external integrations, and infrastructure concerns (C#).               |
| `src/Sentra.Contracts`      | Shared contracts, DTOs, and API models (C#).                                             |
| `src/Sentra.Web`            | Web frontend (Blazor or similar).                                                        |
| `src/Sentra.Rag.*`          | **Python RAG microservices**: `Rag.Server` (vector search), `Rag.Worker` (ingestion).   |
| `src/Sentra.Api.Python`     | Legacy Python API (migration reference, will be deprecated).                             |
| `packages/sentra-rag`       | Python RAG base library: embeddings, vector store, RAG service.                          |
| `packages/sentra-domain`    | Python domain models (legacy, being migrated to C#).                                     |
| `packages/sentra-infra`     | Python infrastructure components (legacy).                                               |
| `deploy/`                   | Docker Compose files, monitoring configs, deployment scripts, and related docs.          |
| `docs/`                     | Technical documentation, ADRs, architecture guides, and internal references.             |
| `data/`                     | Local development data: MongoDB, PostgreSQL, Chroma vector store, RabbitMQ.              |

## Coding Agent Expectations

### 1. **Follow the Hybrid Architecture:**
  - **C# Projects**: All new API endpoints, business logic, domain models, and infrastructure go in `src/` C# projects
  - **Python RAG Services**: RAG-related code stays in Python (`src/Sentra.Rag.*` and `packages/sentra-rag`)
  - These are **independent services** – RAG services communicate with the C# API via HTTP/gRPC
  - Use Microsoft Aspire (`src/Sentra.AppHost`) for service configuration and orchestration

### 2. **C# Development (.NET 10):**
  - **Domain Logic**: Add to `src/Sentra.Domain` (entities, value objects, domain services)
  - **Application Layer**: Add to `src/Sentra.Application` (use cases, application services, orchestration)
  - **API Endpoints**: Add to `src/Sentra.Api` (controllers, minimal APIs, OpenAPI config)
  - **Infrastructure**: Add to `src/Sentra.Infrastructure` (EF Core, repositories, external APIs)
  - **Shared Contracts**: Add to `src/Sentra.Contracts` (DTOs, API models, shared interfaces)
  - **Tests**: Use xUnit, place tests in `src/Sentra.Tests` or alongside projects
  - **Dependencies**: Manage via NuGet, update `.csproj` files
  - **Build & Run**: Use `dotnet run --project src/Sentra.AppHost` or Visual Studio/Rider

### 3. **Python Development (RAG Services Only):**
  - **RAG Services**: Modify `src/Sentra.Rag.Server` or `src/Sentra.Rag.Worker` only for RAG-related features
  - **RAG Library**: Update `packages/sentra-rag` for shared RAG logic (embeddings, vector stores)
  - **Testing**: Use `pytest` for Python services
  - **Dependencies**: Use `requirements.txt` in each Python service directory
  - **Build & Run**: Python services run independently via Docker or `python -m`

### 4. **Microsoft Aspire Integration:**
  - Service registration and configuration happens in `src/Sentra.AppHost/Program.cs`
  - Use Aspire for service discovery, configuration, and observability
  - Add new services to the Aspire host for automatic orchestration
  - Leverage Aspire dashboard for local development monitoring

### 5. **Deployment & Infrastructure:**
  - Use `deploy/` for Docker Compose configurations (dev, staging, prod)
  - Infrastructure services (MongoDB, PostgreSQL, RabbitMQ, Chroma) run via Docker Compose
  - Update `deploy/docker-compose.dev.yml` for local development environments
  - Data persists in `data/` directory for local development

### 6. **Testing Strategy:**
  - **C#**: xUnit for unit/integration tests, run via `dotnet test`
  - **Python**: pytest for RAG services, use VS Code tasks for coverage
  - All tests must pass before merging
  - Integration tests should verify C# ↔ Python service communication

### 7. **Documentation:**
  - Update or add `README.md` in any project/service you modify
  - Central technical docs are in `docs/` (arc42 format, ADRs, use cases)
  - Update `deploy/README.md` for deployment changes

### 8. **Compliance & Privacy:**
  - Never introduce external telemetry or data egress
  - Ensure all data and computation remain local unless explicitly required and documented
  - Follow GDPR, HIPAA, and ISO/IEC 27001 compliance guidelines

### 9. **Pull Requests & Automation:**
  - All code must pass lint, type-check, and tests before merging
  - C# code must follow .NET coding standards and pass code analysis
  - Python code must pass `pytest` and type checking (mypy/pyright)
  - Document any new environment variables or deployment steps

## Quickstart for Agents

### For C# Development (API & Business Logic):

1. **Open the solution:**
   ```bash
   cd src
   dotnet restore Sentra.sln
   # Or open src/Sentra.sln in Visual Studio/Rider
   ```

2. **Run with Microsoft Aspire:**
   ```bash
   dotnet run --project src/Sentra.AppHost
   ```
   This starts all services with the Aspire dashboard at `http://localhost:15888`

3. **Run tests:**
   ```bash
   dotnet test src/Sentra.Tests
   # Or run all tests in solution
   dotnet test src/Sentra.sln
   ```

4. **Add a new feature:**
   - Domain entities → `src/Sentra.Domain`
   - Use cases/services → `src/Sentra.Application`
   - API endpoints → `src/Sentra.Api/Controllers`
   - Data access → `src/Sentra.Infrastructure`

### For Python Development (RAG Services Only):

1. **Install dependencies:**
   ```bash
   cd packages/sentra-rag
   pip install -r requirements.txt
   ```

2. **Run RAG services:**
   ```bash
   cd src/Sentra.Rag.Server
   python -m uvicorn main:app --reload
   ```

3. **Run tests:**
   ```bash
   pytest packages/sentra-rag/tests
   # Or use VS Code task: "pytest: all (coverage)"
   ```

### Full Stack Development:

1. **Start infrastructure services:**
   ```bash
   cd deploy
   docker compose -f docker-compose.dev.yml up -d
   ```
   This starts MongoDB, PostgreSQL, RabbitMQ, and Chroma

2. **Run the complete platform:**
   - Start infrastructure (above)
   - Run Aspire host: `dotnet run --project src/Sentra.AppHost`
   - RAG services will auto-start via Aspire or Docker Compose

## Migration Notes

- **`src/Sentra.Api.Python`**: Legacy Python API kept for reference during migration to C#
- **`packages/sentra-domain`** and **`packages/sentra-infra`**: Legacy Python packages being migrated to C# equivalents
- New features should be implemented in C# unless they are RAG-specific

## Additional Guidance

- **Aspire Configuration**: Check `src/Sentra.AppHost/Program.cs` for service orchestration
- **Environment Variables**: Set in `appsettings.Development.json` for C# or `.env` files for Python services
- **Service Communication**: C# API communicates with Python RAG services via HTTP (OpenAPI contracts)
- **Database Migrations**: Use EF Core migrations in `src/Sentra.Infrastructure`
- For regulatory or compliance changes, update both code and documentation in `docs/`

---

For further details, see the main `README.md` and `docs/`.
