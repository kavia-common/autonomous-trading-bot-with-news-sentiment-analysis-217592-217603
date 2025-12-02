import logging
from datetime import datetime

from sqlalchemy.orm import Session

from src.config.settings import settings
from src.db.models import Trade
from src.services.broker_interface import BrokerInterface
from src.services.broker_paper import PaperBroker
from src.services.broker_zerodha import ZerodhaBroker
from src.services.risk_management import RiskManager

logger = logging.getLogger("trading_bot.trading")


class TradingService:
    """Core orchestrator for trading decisions and execution."""

    def __init__(self):
        # Select broker based on availability of Zerodha keys and token; default to paper
        if settings.ZERODHA_API_KEY and settings.ZERODHA_API_SECRET and settings.ZERODHA_ACCESS_TOKEN:
            self.broker: BrokerInterface = ZerodhaBroker(
                settings.ZERODHA_API_KEY, settings.ZERODHA_API_SECRET, settings.ZERODHA_ACCESS_TOKEN
            )
        else:
            self.broker = PaperBroker()
        self.risk = RiskManager()

    def _get_daily_pnl(self, db: Session) -> float:
        # Very naive PnL: sum over trades' pnl recorded today
        today = datetime.utcnow().date()
        rows = db.query(Trade).all()
        pnl = 0.0
        for t in rows:
            if t.created_at.date() == today and t.pnl:
                pnl += t.pnl
        return pnl

    # PUBLIC_INTERFACE
    def run_trading_cycle(self, db: Session) -> dict:
        """
        Run one trading decision cycle:
        - Generate a trivial signal (placeholder)
        - Apply risk checks
        - Place order via broker
        - Persist trade
        """
        # Placeholder signal: if ENV=development, alternate BUY/SELL, else do nothing without strong sentiment
        symbol = settings.SYMBOLS[0] if settings.SYMBOLS else "NIFTY"
        side = "BUY"
        qty = settings.POSITION_SIZE

        current_daily_pnl = self._get_daily_pnl(db)
        decision = self.risk.can_place_order(current_daily_pnl)
        if not decision.allow:
            logger.info("Risk blocked trade", extra={"reason": decision.reason})
            return {"status": "BLOCKED", "reason": decision.reason}

        broker_resp = self.broker.place_order(symbol=symbol, side=side, qty=qty, price=None)
        status = "PLACED" if broker_resp.status in ("ACCEPTED", "FILLED") else "REJECTED"

        trade = Trade(
            symbol=symbol,
            side=side,
            qty=qty,
            price=None,
            status=status,
            reason="placeholder-signal",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)

        logger.info("Trade recorded", extra={"trade_id": trade.id, "status": status})
        return {"status": status, "order_id": broker_resp.order_id, "trade_id": trade.id}

    # PUBLIC_INTERFACE
    def status(self) -> dict:
        """Return broker connectivity and positions summary (if available)."""
        return {"broker": self.broker.get_profile(), "positions": self.broker.get_positions()}
