# Alembic Migrations Quick Start

This guide covers the essential steps to manage Alembic migrations for the Sentra Brain project.

---

## 1. Initialize Alembic (only once)

Run this from the folder where you want to store your migrations (usually under `libs/sentra-shared/sentra_shared/infra/sql`):

```bash
alembic init alembic
```

This will generate the `alembic.ini` file and an `alembic/` directory with config scripts.

---

## 2. Configure Alembic

Edit `alembic.ini` to remove the hardcoded URL and use an env variable:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

→ Replace it with:

```ini
sqlalchemy.url = env:DATABASE_URL
```

In `alembic/env.py`, import your metadata and assign it:

```python
from sentra_shared.domain.entities.base_entity import BaseEntity

# Use metadata for autogeneration
target_metadata = BaseEntity.metadata
```

You can also use `os.getenv("DATABASE_URL")` if you prefer full control from Python.

---

## 3. Generate a Migration from PowerShell

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://sentra_admin:changeit@127.0.0.1:5432/sentra_brain"
alembic revision --autogenerate -m "Initial schema"
```

This will create a revision script under `alembic/versions/`.

---

## 4. Apply the Migration

To upgrade your database:

```bash
alembic upgrade head
```

To downgrade:

```bash
alembic downgrade -1
```

---

## 5. Remove a Migration

To delete a migration that hasn't been applied yet:

1. Delete the corresponding `.py` file under `alembic/versions/`.
2. Optionally, run `alembic history` to confirm its removal from the chain.

Make sure the migration wasn't applied (`alembic current` should not list it), otherwise you need to downgrade before deleting it.

---

## 6. Pro Tips

* Run `alembic current` to check the current revision.
* Use `alembic history` to view full migration history.
* You can chain environment variables with `.env` loaders if preferred (e.g. `dotenv` in Python or `direnv`/`just`).

---

This workflow makes schema changes safe, repeatable, and traceable. Happy evolving 🧬
