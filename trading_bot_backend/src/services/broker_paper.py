import random
import string
from typing import List

from src.services.broker_interface import BrokerInterface, OrderResponse


class PaperBroker(BrokerInterface):
    """In-memory paper trading implementation for development/testing."""

    def __init__(self):
        self._orders: List[dict] = []
        self._positions: dict[str, int] = {}

    def _gen_order_id(self) -> str:
        return "PAPER-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def place_order(self, symbol: str, side: str, qty: int, price: float | None = None) -> OrderResponse:
        order_id = self._gen_order_id()
        status = "FILLED"
        self._orders.append({"order_id": order_id, "symbol": symbol, "side": side, "qty": qty, "price": price, "status": status})
        sign = 1 if side.upper() == "BUY" else -1
        self._positions[symbol] = self._positions.get(symbol, 0) + sign * qty
        return OrderResponse(order_id=order_id, status=status, message="Simulated order")

    def get_positions(self) -> list[dict]:
        return [{"symbol": s, "qty": q} for s, q in self._positions.items()]

    def get_profile(self) -> dict:
        return {"mode": "paper", "connected": True}
