"""
filter.py — Date and keyword filtering for articles.
"""

from datetime import datetime, timedelta

from config import FINANCE_KEYWORDS
from utils.logger import get_logger
from utils.models import Article

logger = get_logger(__name__)


def _text_relevance_score(text: str) -> int:
    """Count how many finance keywords appear in the text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in FINANCE_KEYWORDS if kw in text_lower)


def filter_by_keywords(articles: list[Article], min_score: int = 1) -> list[Article]:
    """Keep articles whose title + body contain at least `min_score` finance keywords."""
    filtered = []
    for art in articles:
        combined = f"{art.title} {art.body}".lower()
        score = _text_relevance_score(combined)
        if score >= min_score:
            filtered.append(art)
        else:
            logger.debug("Dropped (low relevance): %s", art.title)
    logger.info("Keyword filter: %d → %d articles", len(articles), len(filtered))
    return filtered


def filter_by_date(articles: list[Article], days_back: int = 7) -> list[Article]:
    """
    Keep articles published within the last `days_back` days.
    Articles with no known date are kept (benefit of the doubt).
    """
    cutoff = datetime.now() - timedelta(days=days_back)
    filtered = [
        art for art in articles
        if art.pub_date is None or art.pub_date >= cutoff
    ]
    logger.info("Date filter: %d → %d articles", len(articles), len(filtered))
    return filtered
