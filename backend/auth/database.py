from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import asyncpg
from config import settings

# SQLAlchemy setup
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async database connection for asyncpg
async def get_async_db():
    conn = await asyncpg.connect(settings.database_url)
    try:
        yield conn
    finally:
        await conn.close()
