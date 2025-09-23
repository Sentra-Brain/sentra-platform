> **Community Fair-Use:** Sentra Brain CE is AGPL-3.0.  
> Free **internal use up to 5 seats** per organization; commercial license required beyond that.  
> See **`COMMUNITY-TERMS.md`** and **`LICENSE`**.
# sentra-domain

Canonical **domain & shared types** for Sentra Brain.

This package provides:

* **Canonical models** used across API, runtime, and engine (e.g., `Event`, `ChatRequest`).
* **Domain enums** and value objects.
* **Domain entities** (SQLAlchemy) and **repository ports** (interfaces).
* **Lightweight domain services** (business rules only).

> Goal: one source of truth for domain concepts so streaming, persistence, and APIs use the **same shapes**.

---

## Scope & Non‑Goals

**In scope**

* Canonical **Event** model (for chat/agent streaming) and **ChatRequest**.
* Enums (`EventType`, `Role`, knowledge/document enums, etc.).
* SQLAlchemy entities for relational persistence (users, sessions, documents…).
* Repository **ports** (interfaces) and domain services that depend on ports.

**Out of scope**

* Framework‑specific logic (FastAPI controllers, HTTP schemas).
* Persistence adapters/clients (Mongo/SQL implementations live in infra packages).
* Transport concerns (SSE formatting). Only **pure models** here.

---

## Design Contract (Layering)

```
API (sentra-api) ─┐
ENGINE (sentra-engine) ├──▶  sentra-domain  ◀──┐  RUNTIME (sentra-runtime)
INFRA adapters (sentra-infra) ┘                    (ports implemented here)
```

* Consumers **import** canonical types from `sentra-domain`; they **do not** import from each other.
* Infra implements repository **ports** defined here. Domain services depend on **ports**, not concrete infra.
* Wire (SSE/HTTP) DTOs adapt **format only** (UUID→str, dt→ISO) — never rename fields.

---

## Package Layout

```
sentra-domain/
├── src/
│   └── sentra/
│       └── domain/
│           ├── entities/              # SQLAlchemy entities (relational)
│           ├── enums/                 # Domain enums (Document, Knowledge, Roles, EventType, etc.)
│           ├── models/                # Canonical Pydantic models (Event, ChatRequest, value objects)
│           ├── ports/                 # Abstract repo/service interfaces (no infra deps)
│           ├── services/              # Domain services (use ports)
│           ├── constants/             # Domain constants (no app prompts or UI strings)
│           └── __init__.py
├── tests/
│   ├── unit/
│   └── contracts/                     # Port contract tests (adapter conformance)
├── pyproject.toml
└── README.md
```

> **PEP 420 namespace:** keep `src/sentra/` namespace package; avoid `__init__.py` at `sentra/` root so multiple packages can share it.

---

## Canonical Models (Summary)

### Event (canonical)

* `id: UUID` *(mandatory; equals Mongo `_id` when persisted)*
* `timestamp: datetime` *(aware, UTC)*
* `type: EventType` *(e.g., `user_input`, `message_delta`, `message_final`, `step_start`, `step_error`, …)*
* `role: ChatRole | None` *(user/assistant/system)*
* Optional: `content: str | None`, `task_type`, `task_run_id`, `step_id`, `label`, `status`, `meta: dict = {}`, `actions`, `message`.

**Rules**

* UUIDs are **mandatory**; never generate in mappers — produce at source.
* Persist **all task‑related fields** unmodified.
* Wire adapters only format UUID/datetime; no renames.

### ChatRequest (canonical)

* Single request type used by API → engine/runtime.
* Contains final user message(s), context IDs, user/session IDs, and state.
* **No aliasing** like `ConversationRequest as EngineRequest`.

> Place these under `sentra/domain/models/` to clearly separate them from SQL entities.

---

## Persistence & Serialization Conventions

* **Mongo**: store `_id = str(event.id)`. Optionally store `id` duplicate during migration; aim for only `_id`.
* **SQL**: UUID PKs for entities; timestamps are UTC.
* **Wire (SSE/HTTP)**: `id` as string UUID; `timestamp` in ISO‑8601 UTC.
* **Never** use `event_id`/`author`/`meta.message_id` — use `id`/`role`.

---

## Testing

* Contract tests for repository **ports** (infra adapters must pass the same suite).
* Round‑trip tests for Event: domain → persistence doc → domain (id/time preserved, enums intact).
* Wire formatting tests: domain → wire → domain (no field loss/rename).

---

## Migration Notes (from legacy)

* Replace `event_id` → `id` (UUID). Use `_id=str(id)` in Mongo.
* Replace `author` → `role`.
* Remove `meta.message_id`; use it as `id` instead if present historically.
* Normalize timestamps to aware UTC.

---

## Current TODOs (to align repo with this design)

1. **Models**

* [ ] Move Pydantic `Event` to `domain/models/event.py` with `id/role` and `EventType` enum.
* [ ] Add `domain/models/chat_request.py` and use it across API/engine/runtime.
* [ ] Introduce `enums/event.py` (`EventType`, `ChatRole`).

2. **Rename/Refactor**

* [ ] `event_entity.py` → migrate to canonical `models/event.py`; remove `event_id`/`author`.
* [ ] Avoid duplicate class names: you currently have two `SessionEntity` (SQLAlchemy vs Pydantic). Rename the Pydantic one to `SessionDoc` or move it under `models/`.
* [ ] Move non‑domain app strings (e.g., large `SYSTEM_PROMPT`) **out** of domain (belongs to runtime/config).

3. **Ports & Services**

* [ ] Define Mongo session/event **port** in `domain/ports/session_store.py` (e.g., `append_event`, `get_session_by_id`, `create_session`).
* [ ] Refactor `SessionService` to depend on that port, not import `sentra.infra.*` directly.

4. **Consumers**

* [ ] API schemas/mappers must mirror canonical names (`id`, `role`, `type`).
* [ ] Runtime/Engine event producers must emit `Event` with `id/timestamp` set at source.

---

## Install & Dev

```bash
pip install -e .[dev]
pytest
```

Ensure `PYTHONPATH` includes `src/` in local/CI runs.

---

## Versioning & Compatibility

* Breaking schema changes (e.g., renaming fields) require a minor version bump and a migration note.
* Keep adapters backward‑compatible via one‑off migrations, not by keeping legacy fields in domain models.
