from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderResponse:
    order_id: str
    status: str
    message: Optional[str] = None


class BrokerInterface:
    """
    Abstract broker interface mimicking minimal KiteConnect behavior needed by the app.
    """

    # PUBLIC_INTERFACE
    def place_order(self, symbol: str, side: str, qty: int, price: float | None = None) -> OrderResponse:
        """
        Place an order.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            qty: Quantity
            price: Optional limit price

        Returns:
            OrderResponse: Broker response with order id and status
        """
        raise NotImplementedError

    # PUBLIC_INTERFACE
    def get_positions(self) -> list[dict]:
        """
        Retrieve current positions.

        Returns:
            list[dict]: Positions summary
        """
        raise NotImplementedError

    # PUBLIC_INTERFACE
    def get_profile(self) -> dict:
        """
        Retrieve broker profile or connection status.

        Returns:
            dict: Profile or status details
        """
        raise NotImplementedError
