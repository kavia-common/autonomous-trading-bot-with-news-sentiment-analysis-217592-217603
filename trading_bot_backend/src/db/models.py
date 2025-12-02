from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean

from src.db.base import Base


class Trade(Base):
    """Trade record model."""
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(64), index=True, nullable=False)
    side = Column(String(8), nullable=False)  # BUY/SELL
    qty = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, default="PENDING")
    reason = Column(String(255), nullable=True)
    pnl = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ConfigItem(Base):
    """Key-value configuration storage."""
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
