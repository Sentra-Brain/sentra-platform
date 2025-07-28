# sentra_shared/infra/sql/migrations_check.py

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy.engine import Engine
from alembic import command


def check_schema_consistency(engine: Engine, alembic_ini_path: str = "alembic.ini"):
    """
    Checks if the database schema is consistent with the Alembic migrations.
    This function compares the current database schema revision with the expected revision.
    If there is a mismatch, it raises a RuntimeError indicating the desync.

    Args:
        engine (Engine): SQLAlchemy engine connected to the database.
        alembic_ini_path (str): Path to the alembic.ini file (default: project root).

    Raises:
        RuntimeError: If there is a desync between the schema and the migrations.
    """
    config = Config(alembic_ini_path)
    script = ScriptDirectory.from_config(config)

    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision()
        expected_rev = script.get_current_head()

        if current_rev != expected_rev:
            raise RuntimeError(
                f"❌ Database schema out of sync: current={current_rev}, expected={expected_rev}"
            )

def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")