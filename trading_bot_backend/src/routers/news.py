from typing import List

from fastapi import APIRouter
from src.config.settings import settings
from src.schemas import NewsArticle, NewsQuery
from src.services.sentiment_service import SentimentService

router = APIRouter()


# PUBLIC_INTERFACE
@router.post("/", response_model=List[NewsArticle], summary="Fetch news with sentiment")
def fetch_news(payload: NewsQuery):
    """
    Fetch news via NewsAPI and return naive sentiment-scored articles.

    Args:
        payload (NewsQuery): query, page_size, language
    """
    service = SentimentService(settings.NEWSAPI_KEY)
    return service.fetch_and_score(query=payload.query, page_size=payload.page_size, language=payload.language)
