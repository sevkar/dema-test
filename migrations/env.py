import os
from logging.config import fileConfig

from dotenv import find_dotenv, load_dotenv
from pydantic import PostgresDsn
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

load_dotenv(find_dotenv())
DATABASE_DSN = os.getenv("DATABASE_DSN")

config.set_main_option("sqlalchemy.url", DATABASE_DSN)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
