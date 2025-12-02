import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config.settings import settings
from src.db.base import Base
from src.db import models  # noqa: F401  # ensure models are imported for metadata

logger = logging.getLogger("trading_bot.db")

engine = None
SessionLocal: sessionmaker | None = None


async def init_db() -> None:
    """Initialize database engine and create tables if not present."""
    global engine, SessionLocal
    if engine is not None:
        return
    dsn = settings.sqlalchemy_dsn()
    engine = create_engine(dsn, pool_pre_ping=True, pool_recycle=3600)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized", extra={"component": "db", "dsn": "mysql+pymysql://***@***:***/***"})


async def close_db() -> None:
    """Dispose engine (noop for simple sync engine in this context)."""
    global engine
    if engine is not None:
        engine.dispose()
        engine = None
        logger.info("Database engine disposed", extra={"component": "db"})


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session and ensures proper cleanup.

    Yields:
        Session: SQLAlchemy session
    """
    if SessionLocal is None:
        raise RuntimeError("DB not initialized. Ensure init_db() is called in lifespan.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
