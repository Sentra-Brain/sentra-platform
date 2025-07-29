# alembic/env.py

from logging.config import fileConfig
import os
import pkgutil
import importlib

from sqlalchemy import Enum as PgEnum
from sqlalchemy import MetaData
from sqlalchemy import create_engine, pool
from alembic import context

# Auto-import all modules in sentra_shared.domain.entities
import sentra_shared.domain.entities
import sentra_shared.domain.enums
for _, module_name, _ in pkgutil.iter_modules(sentra_shared.domain.entities.__path__):
    importlib.import_module(f"sentra_shared.domain.entities.{module_name}")
for _, module_name, _ in pkgutil.iter_modules(sentra_shared.domain.enums.__path__):
    importlib.import_module(f"sentra_shared.domain.enums.{module_name}")

from sentra_shared.domain.entities.base_entity import BaseEntity

# Alembic config object
config = context.config

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tell Alembic where the models are
target_metadata = BaseEntity.metadata

# Get DB connection from env var
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("Missing DATABASE_URL environment variable")

def create_enums(connection, metadata:MetaData):
    created = set()
    for table in metadata.tables.values():
        for column in table.columns:
            enum_type = column.type
            if isinstance(enum_type, PgEnum):
                if enum_type.name not in created:
                    enum_type.create(bind=connection, checkfirst=True)
                    created.add(enum_type.name)

def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(DB_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            create_enums(connection, target_metadata)
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
