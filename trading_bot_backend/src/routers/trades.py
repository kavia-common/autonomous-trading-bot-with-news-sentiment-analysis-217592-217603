from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.models import Trade
from src.db.session import get_db
from src.schemas import TradeCreate, TradeRead

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", response_model=List[TradeRead], summary="List trades")
def list_trades(db: Session = Depends(get_db)):
    """
    List all trades recorded in the database.
    """
    return db.query(Trade).order_by(Trade.created_at.desc()).all()


# PUBLIC_INTERFACE
@router.post("/", response_model=TradeRead, summary="Create trade (manual)")
def create_trade(payload: TradeCreate, db: Session = Depends(get_db)):
    """
    Create a trade entry manually. Useful for testing DB and API.

    Args:
        payload (TradeCreate): Trade payload

    Returns:
        TradeRead: Created trade record
    """
    trade = Trade(
        symbol=payload.symbol,
        side=payload.side,
        qty=payload.qty,
        price=payload.price,
        status="MANUAL",
        reason=payload.reason,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade
