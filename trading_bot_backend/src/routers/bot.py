from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.trading_service import TradingService

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/status", summary="Bot status")
def bot_status():
    """
    Get bot and broker status including positions.

    Returns:
        dict: broker connectivity and positions
    """
    service = TradingService()
    return service.status()


# PUBLIC_INTERFACE
@router.post("/run", summary="Run trading cycle once")
def run_cycle(db: Session = Depends(get_db)):
    """
    Trigger a single trading cycle manually.

    Args:
        db (Session): Injected database session

    Returns:
        dict: Result of the trading cycle (status, trade_id, etc.)
    """
    service = TradingService()
    return service.run_trading_cycle(db)
