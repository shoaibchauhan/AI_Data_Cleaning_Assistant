# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.database import DATABASE_URL  # Import your async DATABASE_URL from app/database.py
from app.models import Base  # Import the Base for models

# This line sets up logging as defined in your INI file.
fileConfig(context.config.config_file_name)

# Get the database URL from the config
config = context.config

# Create the async engine using `create_async_engine`
connectable = create_async_engine(DATABASE_URL, echo=True)

# Modify this to work asynchronously
def run_migrations_online():
    # Start a transaction in the async connection context
    with connectable.connect() as connection:
        # Here we use the async method `run_sync` to handle migrations
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()
