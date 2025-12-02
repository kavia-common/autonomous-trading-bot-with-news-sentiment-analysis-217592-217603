import logging
from typing import List, Optional

import httpx

from src.schemas import NewsArticle

logger = logging.getLogger("trading_bot.sentiment")

POSITIVE_WORDS = {"beat", "beats", "surge", "soar", "rally", "gain", "up", "bull", "positive", "growth", "profit", "strong"}
NEGATIVE_WORDS = {"miss", "falls", "slump", "plunge", "down", "bear", "negative", "loss", "weak", "fraud", "scam", "lawsuit"}


class SentimentService:
    """Fetches news via NewsAPI and performs a naive sentiment score."""

    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key

    def _score(self, text: str) -> float:
        text_l = text.lower()
        pos = sum(word in text_l for word in POSITIVE_WORDS)
        neg = sum(word in text_l for word in NEGATIVE_WORDS)
        score = 0.0
        if pos or neg:
            score = (pos - neg) / max(pos + neg, 1)
        return max(-1.0, min(1.0, score))

    # PUBLIC_INTERFACE
    def fetch_and_score(self, query: str, page_size: int = 10, language: str = "en") -> List[NewsArticle]:
        """
        Fetch news from NewsAPI and compute simple sentiment score.

        Args:
            query: Search query
            page_size: Number of results
            language: Language code

        Returns:
            List[NewsArticle]: Articles with sentiment
        """
        if not self.api_key:
            logger.warning("NewsAPI key missing; returning empty articles", extra={"component": "sentiment"})
            return []

        url = "https://newsapi.org/v2/everything"
        params = {"q": query, "pageSize": page_size, "language": language, "sortBy": "publishedAt"}
        headers = {"X-Api-Key": self.api_key}
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.error("NewsAPI request failed", extra={"component": "sentiment", "error": str(exc)})
            return []

        articles = []
        for item in data.get("articles", []):
            title = item.get("title") or ""
            description = item.get("description") or ""
            content = item.get("content") or ""
            combined = " ".join([title, description, content]).strip()
            score = self._score(combined)
            articles.append(
                NewsArticle(
                    title=title,
                    url=item.get("url") or "",
                    source=(item.get("source") or {}).get("name") or "unknown",
                    published_at=item.get("publishedAt"),
                    sentiment=score,
                )
            )
        return articles
