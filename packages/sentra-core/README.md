# sentra-core

**Shared domain, infrastructure, and utility code** for Sentra Brain.

This package defines core entities, domain services, database access, and shared components used across the system.

## 📦 Package Layout

```
sentra-core/
├── src/
│   └── sentra/
│       ├── domain/              # Business logic and domain entities
│       │   ├── constants/       # Domain-specific constants
│       │   ├── entities/        # Core domain entities (user, org, etc.)
│       │   ├── enums/           # Enumerations used in domain models
│       │   ├── repository/      # Domain repository interfaces (SQL/Mongo)
│       │   ├── services/        # Domain-level logic (e.g., permission checks)
│       │   └── role.py          # Example domain entity or logic
│       ├── infra/               # Infrastructure: SQL, Mongo, messaging, auth
│       │   ├── sql/             # Postgres + SQLAlchemy adapters
│       │   ├── nosql/           # Mongo adapters (e.g., messages, sessions)
│       │   └── messaging/       # RabbitMQ publishing helpers
│       ├── model/               # Shared DTOs or internal representations
│       ├── schemas/             # Pydantic request/response models
│       └── shared/              # Logging, settings, constants
│           ├── logging.py
│           ├── settings.py
│           ├── constants.py
│           └── ...
├── tests/
│   ├── domain/
│   ├── core/
│   ├── conftest.py              # Pytest configuration
│   └── .env.test                # Local test config
├── pyproject.toml               # Build system and dependencies
├── README.md
└── ...
```

### ✅ Key Concepts

* **PEP 420 namespace package**: No `__init__.py` at `src/sentra/`. This enables multiple packages (e.g., `sentra-core`, `sentra-rag`, `sentra-runtime`) to share the same `sentra.*` namespace.

* **Clean Architecture layering**:

  * `domain/`: Pure business logic and entities, independent of tech.
  * `infra/`: Infrastructure implementations (Postgres, Mongo, etc).
  * `shared/`: Logging, config, constants reused across services.
  * `schemas/` + `model/`: API-bound and internal data models, respectively.

### 🧪 Running Tests

Install the package in editable mode and run tests:

```bash
pip install -e .[dev]
pytest
```

> ⚠️ Make sure `PYTHONPATH` includes `src/` when running tests locally or in CI.
