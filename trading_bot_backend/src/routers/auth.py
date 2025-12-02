from fastapi import APIRouter, HTTPException
from src.config.settings import settings

router = APIRouter(prefix="/zerodha")


# PUBLIC_INTERFACE
@router.get("/login_url", summary="Get Zerodha login URL (stub)")
def get_login_url():
    """
    Return the stubbed login URL for Zerodha OAuth.

    Returns:
        dict: login_url
    """
    if not (settings.ZERODHA_API_KEY and settings.ZERODHA_REDIRECT_URL):
        raise HTTPException(status_code=400, detail="Zerodha API key or redirect URL not configured")
    # Real URL: f"https://kite.trade/connect/login?v=3&api_key={settings.ZERODHA_API_KEY}"
    return {"login_url": f"https://kite.trade/connect/login?v=3&api_key={settings.ZERODHA_API_KEY}"}


# PUBLIC_INTERFACE
@router.get("/callback", summary="Handle Zerodha callback (stub)")
def handle_callback(request_token: str):
    """
    Handle Zerodha OAuth callback (stub). In real integration, exchange request_token for access_token.

    Args:
        request_token (str): token provided by Zerodha after login

    Returns:
        dict: simulated access token persistence note
    """
    # Here you'd use kite.generate_session(request_token, api_secret) to get access_token
    # For now, just echo the token as placeholder
    return {"status": "ok", "request_token": request_token, "note": "Exchange this for access_token in real integration"}
