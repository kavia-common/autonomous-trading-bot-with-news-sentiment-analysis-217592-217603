from dataclasses import dataclass

from src.config.settings import settings


@dataclass
class RiskDecision:
    allow: bool
    reason: str | None = None


class RiskManager:
    """Simple risk management rules."""

    # PUBLIC_INTERFACE
    def can_place_order(self, current_daily_pnl: float, risk_per_trade: float | None = None) -> RiskDecision:
        """
        Determine if a new order can be placed based on configured limits.

        Args:
            current_daily_pnl: Current realized PnL for the day (negative indicates loss)
            risk_per_trade: Optional per-trade risk override

        Returns:
            RiskDecision: Whether order is allowed and reason if blocked
        """
        if current_daily_pnl <= -abs(settings.MAX_DAILY_LOSS):
            return RiskDecision(False, f"Daily loss limit reached: {current_daily_pnl} <= -{settings.MAX_DAILY_LOSS}")
        rpt = risk_per_trade or settings.MAX_TRADE_RISK
        if rpt > settings.MAX_TRADE_RISK:
            return RiskDecision(False, f"Risk per trade {rpt} exceeds max {settings.MAX_TRADE_RISK}")
        return RiskDecision(True)
