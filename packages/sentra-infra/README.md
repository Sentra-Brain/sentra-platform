> **Community Fair-Use:** Sentra Brain CE is AGPL-3.0.  
> Free **internal use up to 5 seats** per organization; commercial license required beyond that.  
> See **`COMMUNITY-TERMS.md`** and **`LICENSE`**.
# sentra-infra

**Infrastructure adapters** for Sentra Brain.

This package contains the concrete implementations of infrastructure concerns: SQL databases, MongoDB, messaging, and external integrations. It depends on **sentra-domain** for canonical entities, enums, and repository ports.

## 📦 Package Layout

```
sentra-infra/
├── src/
│   └── sentra/
│       └── infra/
│           ├── sql/             # Postgres + SQLAlchemy adapters (implement domain repos)
│           ├── nosql/           # MongoDB adapters (sessions, events, chat history)
│           ├── messaging/       # RabbitMQ/AMQP publishers and consumers
│           ├── auth/            # Auth providers (optional)
│           └── __init__.py
├── tests/
│   ├── sql/
│   ├── nosql/
│   ├── messaging/
│   └── conftest.py
├── pyproject.toml
└── README.md
```

### ✅ Key Concepts

* **Dependency direction**: `sentra-infra` **depends on** `sentra-domain`. The domain layer never imports from infra.

* **Ports & Adapters**:

  * Repository **ports** are defined in `sentra-domain`.
  * Their **adapters** live here (SQLAlchemy, MongoDB, etc.).

* **Isolation**: No business rules here — only persistence, messaging, and integration code.

---

## 🧪 Running Tests

Install the package in editable mode and run tests:

```bash
pip install -e .[dev]
pytest
```

> ⚠️ Ensure `PYTHONPATH` includes `src/` when running tests locally or in CI.

---

## Relation to Other Packages

* **sentra-domain** → canonical entities, enums, repository ports, and business services.
* **sentra-infra** → concrete implementations of those ports (SQL, Mongo, RabbitMQ, etc.).
* **sentra-api / sentra-runtime / sentra-engine** → import ports from `sentra-domain`, use adapters from `sentra-infra` via dependency injection.
