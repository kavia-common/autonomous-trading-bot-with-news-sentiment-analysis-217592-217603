from typing import Optional

from src.services.broker_interface import BrokerInterface, OrderResponse


class ZerodhaBroker(BrokerInterface):
    """
    Lightweight stub that mimics Zerodha integration points.

    Note: Real integration requires official kiteconnect library and login flow to obtain access_token.
    """

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], access_token: Optional[str]):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token

    def _connected(self) -> bool:
        return bool(self.api_key and self.api_secret and self.access_token)

    def place_order(self, symbol: str, side: str, qty: int, price: float | None = None) -> OrderResponse:
        if not self._connected():
            return OrderResponse(order_id="N/A", status="REJECTED", message="Not authenticated with Zerodha")
        # Placeholder: Implement actual kite.place_order here
        return OrderResponse(order_id="KITE-PLACEHOLDER", status="ACCEPTED", message="Order accepted (stub)")

    def get_positions(self) -> list[dict]:
        if not self._connected():
            return []
        # Placeholder: return empty for now
        return []

    def get_profile(self) -> dict:
        return {"mode": "zerodha", "connected": self._connected()}
