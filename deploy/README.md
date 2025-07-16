# Deploy

This directory contains deployment scripts, manifests, and configuration files for deploying the Sentra Brain system.

---

## Deployment Overview

- Docker Compose files for local development and production deployments.
- Environment variable files (`.dev.env`) used across services.
- Volume and network configuration for persistence and service discovery.
- Supports self-hosted and hybrid deployment models as described in `/docs/arc42/07_deployment_view.md`.

---

## Core Services and Ports

| Service Name       | Purpose                                | Port  | Image                                      |
|--------------------|----------------------------------------|-------|---------------------------------------------|
| sentra-web         | Chat UI                                | 3000  | Custom build (React/Next.js)                |
| sentra-admin       | Admin UI                               | 3001  | Custom build (React/Next.js)                |
| sentra-api         | Orchestrator + API + Auth + MCP Client | 8000  | Custom (Python/Node.js)                     |
| llama-server       | LLM Backend                            | 11434 | ghcr.io/ggml-org/llama.cpp:server-cuda      |
| sentra-vector-db   | Vector Store (RAG)                     | 8001  | ghcr.io/chroma-core/chroma:latest           |
| sentra-sql-db      | SQL Persistent Storage (Users/Configs) | 5432  | postgres:16-alpine                          |
| sentra-nosql-db    | NoSQL Chat History Storage             | 27017 | mongo:7                                     |
| sentra-doc         | MCP: Document Search Tools            | 5001  | Custom MCP server                            |
| sentra-crm         | MCP: CRM Lookup Tools                 | 5002  | Custom MCP server                            |
| sentra-action      | MCP: Email/Actions                    | 5003  | Custom MCP server                            |

---

## Developer Notes

- Use `docker-compose.dev.yml` for local development with live reload and mounted volumes.
- Use `docker-compose.yml` for deployment with pre-built images.
- Environment variables are centralized in `.dev.env`.
- GPU passthrough for `llama-server` is required both in production and local development.
  - Ensure NVIDIA drivers and Docker NVIDIA runtime are installed.
  - For WSL2: install CUDA Toolkit inside WSL.
  - For Linux/Mac: `nvidia-container-toolkit` must be configured.

See the full deployment guide in `/docs/arc42/07_deployment_view.md` for advanced configurations.
