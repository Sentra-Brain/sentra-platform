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

| Service Name     | Purpose                                | Port  | Image                                  |
| ---------------- | -------------------------------------- | ----- | -------------------------------------- |
| sentra-web       | Chat UI                                | 3100  | Custom build (React/Next.js)           |
| sentra-admin     | Admin UI                               | 3001  | Custom build (React/Next.js)           |
| sentra-api       | Orchestrator + API + Auth + MCP Client | 8100  | Custom (Python/Node.js)                |
| llama-server     | LLM Backend                            | 11434 | ghcr.io/ggml-org/llama.cpp:server-cuda |
| sentra-vector-db | Vector Store (RAG)                     | 8001  | ghcr.io/chroma-core/chroma:latest      |
| sentra-sql-db    | SQL Persistent Storage (Users/Configs) | 5432  | postgres:16-alpine                     |
| sentra-nosql-db  | NoSQL Chat History Storage             | 27017 | mongo:7                                |
| sentra-action    | MCP: Email/Actions                     | 5003  | Custom MCP server                      |

---

## Developer Notes

- Use `docker-compose.dev.yml` for local development with live reload and mounted volumes.
- Use `docker-compose.yml` for deployment with pre-built images.
- Environment variables are centralized in `.dev.env`.
- GPU passthrough for `llama-server` is required both in production and local development:
  - Ensure NVIDIA drivers and Docker NVIDIA runtime are installed.
  - For WSL2: install CUDA Toolkit inside WSL.
  - For Linux/Mac: `nvidia-container-toolkit` must be configured.

---

### LLM Model Setup for Local Development

- The `llama-server` container **requires a GGUF model file** mounted via Docker volume.
- By default, **no model is included** in the repository or Docker images for licensing and size reasons.
- Each developer must manually download a GGUF model from Hugging Face and mount it locally.

#### Recommended Small Models for Development

| Model                                       | Size    | Suggested Use            |
| ------------------------------------------- | ------- | ------------------------ |
| TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF      | ~1.8 GB | Fast local debugging     |
| TheBloke/phi-2-GGUF                         | ~2–4 GB | General testing          |
| TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF | ~7–8 GB | Balanced (A6000 capable) |

#### How to Download a Model (Example)

1. Install Hugging Face CLI:
   ```bash
   pip install -U "huggingface_hub[cli]"
   huggingface-cli login
   ```
2. Download:

    ```bash
    huggingface-cli download TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF --local-dir D:\models\tiny-llama
    ```

3. Update docker-compose.dev.yml:

    ```docker
    volumes:
        - D:\models:/models:ro
    command: >
        -m /models/tiny-llama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
        --port 11434
        --host 0.0.0.0
    ```

## Accessing Sentra Web and Admin in Production

- The following ports are exposed for LAN access:
  - `http://<server-ip>:3100` → Sentra Web (User Chat UI)
  - `http://<server-ip>:3001` → Sentra Admin (Admin Panel)

- No public internet exposure is assumed by default.

- For secured access, it is recommended to place a reverse proxy (e.g., NGINX or Traefik) in front of Sentra Web and Sentra Admin:
  - Handles SSL termination (HTTPS).
  - Controls IP allowlists or VPN access.

- Database and internal services are only exposed inside the Docker network (`sentrabrain-net`).

