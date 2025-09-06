---
# Sentra Brain – Agent Coding Guide (2025)

## Overview

Sentra Brain is a modular, private AI server platform for professional environments needing compliance, privacy, and control. It is organized as a monorepo with clear separation between core packages, services, deployment, and frontends.

All code, data, and computation are designed to remain on-premises. The system is built for extensibility, regulatory compliance (GDPR, HIPAA, ISO/IEC 27001), and modularity.

## Monorepo Structure

| Path                        | Purpose                                                                                 |
|-----------------------------|-----------------------------------------------------------------------------------------|
| `packages/sentra-core`      | Core domain logic, models, infrastructure, and tests.                                    |
| `packages/sentra-rag`       | RAG (Retrieval Augmented Generation) base library: embeddings, vector store, RAG service.|
| `packages/sentra-runtime`   | Runtime logic, orchestration, and supporting libraries.                                  |
| `services/sentra-api`       | Main API gateway (REST), orchestrates core, integrates with DBs and vector stores.       |
| `services/sentra-mcp`       | MCP (Model Context Protocol) server for external integrations and long-running ops.       |
| `services/sentra-rag-*`     | Microservices for vector search (`server`) and document ingestion (`worker`).            |
| `deploy/`                   | Docker Compose files, monitoring configs, deployment scripts, and related docs.          |
| `frontends/`                | Web UIs: `sentra-admin` (admin panel), `sentra-web` (end-user chat).                    |
| `docs/`                     | Technical documentation, ADRs, and internal guides.                                      |
| `website/`                  | Public marketing site and documentation.                                                 |

## Coding Agent Expectations

1. **Follow Monorepo Conventions:**
  - Place new core logic in the appropriate `packages/` subfolder.
  - Add new services to `services/` with their own code, tests, and requirements.
  - Use `deploy/` for all deployment, Docker, and monitoring config changes.
  - Frontend changes go in `frontends/`.

2. **Testing:**
  - Each package/service has its own `tests/` directory. Add or update tests alongside code changes.
  - Run tests using `pytest` from the root or the relevant subfolder.
  - Use the provided VS Code tasks for full coverage and CI parity.

3. **Dependencies:**
  - Python packages: use `pyproject.toml` (for packages) or `requirements.txt` (for services).
  - Node.js frontends: use `package.json` in the relevant frontend folder.

4. **Build & Run:**
  - Use Docker Compose from `deploy/` for local/dev/prod environments.
  - Each service/package can be run and tested independently if needed.

5. **Documentation:**
  - Update or add `README.md` in any package/service you modify.
  - Central docs are in `docs/` and `deploy/README.md`.

6. **Compliance & Privacy:**
  - Never introduce external telemetry or data egress.
  - Ensure all data and computation remain local unless explicitly required and documented.

7. **Pull Requests & Automation:**
  - All code must pass lint, type-check, and tests before merging.
  - Run all relevant tests and build steps locally before PR.
  - Document any new environment variables or deployment steps in the appropriate `README.md` or `deploy/` docs.

## Quickstart for Agents

1. **Clone and prepare:**
  ```bash
  git clone <repo-url>
  cd sentra-brain
  ```
2. **Install dependencies:**
  - For a Python package:
    ```bash
    cd packages/sentra-core
    pip install -r requirements.txt  # or poetry install
    ```
  - For a service:
    ```bash
    cd services/sentra-api
    pip install -r requirements.txt
    ```
  - For a frontend:
    ```bash
    cd frontends/sentra-admin
    npm install
    ```
3. **Run tests:**
  ```bash
  pytest packages/sentra-core/tests
  pytest services/sentra-api/tests
  # or use VS Code tasks for full coverage
  ```
4. **Build and run locally:**
  ```bash
  cd deploy
  docker compose -f docker-compose.dev.yml up --build
  ```

## Additional Guidance

- Always check `.env` files and update as needed for new features.
- If you add a new service or package, ensure it is documented and included in the appropriate Docker Compose file if needed.
- For regulatory or compliance changes, update both code and documentation.

---

For further details, see the main `README.md` and `docs/`.
