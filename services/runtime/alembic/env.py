"""Alembic environment configuration."""

import asyncio
from logging.config import fileConfig
from typing import Any

from sqlalchemy import MetaData, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from yaga_runtime.config import RuntimeSettings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override alembic.ini URL with the config model's database_url.
runtime_settings = RuntimeSettings()
config.set_main_option("sqlalchemy.url", runtime_settings.database_url)

# Shared metadata — ORM models register on this as they are added.
# Empty for now; the first real migration will populate it.
target_metadata = MetaData()


def run_migrations_offline() -> None:
    """Run migrations in offline mode (generates SQL script)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Any) -> None:
    """Run migrations against a live connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in online mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
