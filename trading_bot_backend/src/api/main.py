import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings, get_settings_summary
from src.core.logging_config import configure_logging
from src.db.session import init_db, close_db
from src.routers.bot import router as bot_router
from src.routers.config import router as config_router
from src.routers.trades import router as trades_router
from src.routers.news import router as news_router
from src.routers.auth import router as auth_router
from src.scheduler.trading_scheduler import TradingScheduler
from src.services.sentiment_service import SentimentService

# Configure structured logging early
configure_logging()
logger = logging.getLogger("trading_bot")
settings = get_settings()

# Global scheduler instance
trading_scheduler: TradingScheduler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context:
    - Initialize DB connection
    - Start trading loop scheduler (if enabled)
    - Warm up services as needed
    - Cleanup on shutdown
    """
    global trading_scheduler
    logger.info("Starting application lifespan initialization", extra={"component": "lifespan"})
    await init_db()

    # Warm-up cache for sentiment categories if desired
    SentimentService(settings.NEWSAPI_KEY)  # instantiate to validate key (optional)

    # Start scheduler if enabled
    if settings.SCHEDULER_ENABLED:
        trading_scheduler = TradingScheduler()
        trading_scheduler.start()
        logger.info("Trading scheduler started", extra={"component": "scheduler"})
    else:
        logger.info("Trading scheduler disabled by settings", extra={"component": "scheduler"})

    yield

    # Teardown
    if trading_scheduler:
        trading_scheduler.stop()
        logger.info("Trading scheduler stopped", extra={"component": "scheduler"})
    await close_db()
    logger.info("Application lifespan shutdown complete", extra={"component": "lifespan"})


openapi_tags: List[dict] = [
    {"name": "Health", "description": "Service health and metadata"},
    {"name": "Bot", "description": "Control and status of the trading bot"},
    {"name": "Config", "description": "Read and update runtime configuration"},
    {"name": "Trades", "description": "Trade records, orders and history"},
    {"name": "News", "description": "News and sentiment analysis"},
    {"name": "Auth", "description": "Authentication flows for broker integrations (e.g., Zerodha)"},
    {"name": "WebSocket", "description": "Real-time interfaces and usage notes"},
]

app = FastAPI(
    title="Autonomous Trading Bot Backend",
    description="Backend for an autonomous futures & options trading bot integrating Zerodha (KiteConnect) and NewsAPI for sentiment.",
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """
    Health check endpoint.

    Returns:
        dict: {"message": "Healthy", "settings": {...}} with sanitized settings summary.
    """
    return {"message": "Healthy", "settings": get_settings_summary()}


# PUBLIC_INTERFACE
@app.get("/docs/websocket", tags=["WebSocket"], summary="WebSocket usage notes")
def websocket_usage():
    """
    Provide WebSocket usage notes for real-time updates.

    Returns:
        dict: Basic websocket connection info for clients.
    """
    return {
        "note": "This backend currently does not expose WebSocket endpoints. "
                "For real-time updates, consider Server-Sent Events (SSE) or add WS later.",
        "recommendation": "Use /trades/stream (future) or poll /trades for updates.",
    }


# Register routers
app.include_router(bot_router, prefix="/bot", tags=["Bot"])
app.include_router(config_router, prefix="/config", tags=["Config"])
app.include_router(trades_router, prefix="/trades", tags=["Trades"])
app.include_router(news_router, prefix="/news", tags=["News"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
