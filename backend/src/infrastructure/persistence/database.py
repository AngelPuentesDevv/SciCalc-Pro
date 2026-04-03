from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
import sys

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc"
)

# On Windows, asyncpg 0.31.x has a bug with sslmode=prefer (the default):
# when the server returns 'N' (no SSL), the ConnectionReset during the SSL
# negotiation is not caught as a retryable signal, and the connection fails.
# Fix: pass ssl=False via connect_args so asyncpg never attempts SSL negotiation.
_connect_args = {}
if sys.platform == "win32":
    _connect_args["ssl"] = False

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

AsyncSessionFactory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
