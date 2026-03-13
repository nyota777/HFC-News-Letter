"""
cleaner.py — Clean text from articles and orchestrate the processing pipeline.
"""

import re
from utils.logger import get_logger
from utils.models import Article

# Import filtering and deduping logic so we can run them all from here
from processing.filter import filter_by_date, filter_by_keywords
from processing.deduplicator import deduplicate

logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """
    Light text cleaning:
    - Collapse excessive whitespace
    - Remove non-printable characters
    - Strip common boilerplate phrases
    """
    if not text:
        return ""
    
    # Remove non-printable chars
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    # Remove common boilerplate patterns
    boilerplate = [
        r"subscribe to our newsletter.*",
        r"sign up for.*alerts.*",
        r"advertisement",
        r"read more:.*",
        r"also read:.*",
        r"click here to.*",
        r"follow us on.*",
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
    return text.strip()


def clean_articles(articles: list[Article]) -> list[Article]:
    """Apply clean_text to each article's body in-place."""
    for art in articles:
        if art.body:
            art.body = clean_text(art.body)
    return articles


def run_pipeline(articles: list[Article], days_back: int = 7) -> list[Article]:
    """Run the full cleaning pipeline: date filter → keyword filter → dedup → clean."""
    articles = filter_by_date(articles, days_back)
    articles = filter_by_keywords(articles)
    articles = deduplicate(articles)
    articles = clean_articles(articles)
    logger.info("Cleaning pipeline complete. Final count: %d articles", len(articles))
    return articles
