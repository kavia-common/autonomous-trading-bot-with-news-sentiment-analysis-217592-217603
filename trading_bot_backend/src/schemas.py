from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    symbol: str = Field(..., description="Trading symbol, e.g., NIFTY")
    side: str = Field(..., description="BUY or SELL")
    qty: int = Field(ge=1, default=1)
    price: Optional[float] = Field(default=None, description="Limit price if applicable")
    reason: Optional[str] = Field(default=None, description="Reason for trade")


class TradeRead(BaseModel):
    id: int
    symbol: str
    side: str
    qty: int
    price: Optional[float] = None
    status: str
    reason: Optional[str] = None
    pnl: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigItemCreate(BaseModel):
    key: str
    value: Any


class ConfigItemRead(BaseModel):
    id: int
    key: str
    value: Any
    updated_at: datetime
    active: bool

    class Config:
        from_attributes = True


class NewsArticle(BaseModel):
    title: str
    url: str
    source: str
    published_at: Optional[str] = None
    sentiment: float = Field(..., description="Sentiment score in range [-1,1] where positive is bullish")


class NewsQuery(BaseModel):
    query: str
    page_size: int = Field(default=10, ge=1, le=100)
    language: str = Field(default="en")
