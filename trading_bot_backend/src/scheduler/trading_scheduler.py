import logging
import threading
import time

from src.config.settings import settings
from src.db.session import get_db
from src.services.trading_service import TradingService

logger = logging.getLogger("trading_bot.scheduler")


class TradingScheduler:
    """Background thread scheduler for periodic trading loop."""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._service = TradingService()

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                with next(get_db()) as db:
                    self._service.run_trading_cycle(db)
            except Exception as exc:
                logger.error("Error in trading cycle", extra={"error": str(exc)})
            # Sleep for configured interval
            for _ in range(settings.SCHEDULER_INTERVAL_SECONDS):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    # PUBLIC_INTERFACE
    def start(self):
        """Start the background scheduler thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, name="trading-scheduler", daemon=True)
        self._thread.start()

    # PUBLIC_INTERFACE
    def stop(self):
        """Stop the scheduler and join the thread."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=5)
