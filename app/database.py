# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

# Database URL
DATABASE_URL = "postgresql+asyncpg://postgres:hello@localhost:5432/cleaning_db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# AsyncSessionLocal for session management
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
