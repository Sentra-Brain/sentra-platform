-- DROP ALL TABLES in current schema (e.g., "public")
-- ⚠️ USE WITH CAUTION: this is irreversible
-- Recommended for dev/test environments only

-- ⚠️ Este script eliminará todos los datos y las tablas en orden

-- Step 1: Truncate tables
-- This will remove all rows from the specified tables without dropping them
TRUNCATE TABLE
    conversations,
    documents,
    knowledge_sources,
    system_settings,
    users,
    alembic_version
CASCADE;

-- Step 2: Delete tables
-- This will drop all tables in the current schema, including any foreign key constraints
DROP TABLE IF EXISTS
    conversations,
    documents,
    knowledge_sources,
    system_settings,
    users,
    alembic_version
CASCADE;


-- Step 3: Drop all tables and sequences in the current schema
-- This will remove all tables and sequences in the current schema, including any foreign key constraints
DO $$
DECLARE
    rec RECORD;
BEGIN
    -- Confirm current schema (usually 'public')
    RAISE NOTICE 'Dropping all tables in schema: %', current_schema();

    -- Loop through all tables
    FOR rec IN (
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = current_schema()
    ) LOOP
        EXECUTE format('DROP TABLE IF EXISTS %I CASCADE;', rec.tablename);
        RAISE NOTICE 'Dropped table: %', rec.tablename;
    END LOOP;
END
$$;

DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN (
        SELECT sequence_name FROM information_schema.sequences
        WHERE sequence_schema = current_schema()
    ) LOOP
        EXECUTE format('DROP SEQUENCE IF EXISTS %I CASCADE;', rec.sequence_name);
        RAISE NOTICE 'Dropped sequence: %', rec.sequence_name;
    END LOOP;
END
$$;
