# autonomous-trading-bot-with-news-sentiment-analysis-217592-217603

Backend (FastAPI) for trading bot is located in trading_bot_backend/.

Quick start:
1) cp trading_bot_backend/.env.example trading_bot_backend/.env
2) Edit DB and API keys as needed (see .env.example).
3) Install deps: pip install -r trading_bot_backend/requirements.txt
4) Run: uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload --app-dir trading_bot_backend
   - Or from trading_bot_backend dir: uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
5) Generate OpenAPI: python -m src.api.generate_openapi

Key endpoints:
- GET /               Health and settings summary
- GET /bot/status     Bot & broker status
- POST /bot/run       Trigger one trading cycle
- GET /trades         List trades
- POST /trades        Create trade manually
- GET /auth/zerodha/login_url   Get OAuth login url (stub)
- GET /auth/zerodha/callback    Handle OAuth callback (stub)
- POST /news          Fetch news with naive sentiment

Note: Real Zerodha trading requires kiteconnect library and OAuth; current build ships a paper trading stub by default.