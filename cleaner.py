"""
cleaner.py — Clean, filter, and deduplicate article data.
"""

import re
import logging
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Optional

logger = logging.getLogger(__name__)

# ── Finance / banking keyword filter ─────────────────────────────────────────
FINANCE_KEYWORDS = [
    "bank", "banking", "mortgage", "interest rate", "loan", "inflation",
    "credit", "central bank", "fintech", "housing finance", "regulation",
    "investment", "bond", "equity", "stock", "market", "economy", "economic",
    "monetary", "fiscal", "treasury", "forex", "exchange rate", "gdp",
    "insurance", "pension", "deposit", "lending", "borrowing", "liquidity",
    "capital", "asset", "liability", "revenue", "profit", "loss",
    "microfinance", "sacco", "nse", "nairobi securities exchange",
    "kenya shilling", "kes", "imf", "world bank", "cbk",
]


def _text_relevance_score(text: str) -> int:
    """Count how many finance keywords appear in the text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in FINANCE_KEYWORDS if kw in text_lower)


def filter_by_keywords(articles: list, min_score: int = 1) -> list:
    """Keep articles whose title + body contain at least `min_score` finance keywords."""
    filtered = []
    for art in articles:
        combined = f"{art.title} {getattr(art, 'body', '')}".lower()
        score = _text_relevance_score(combined)
        if score >= min_score:
            filtered.append(art)
        else:
            logger.debug("Dropped (low relevance): %s", art.title)
    logger.info("Keyword filter: %d → %d articles", len(articles), len(filtered))
    return filtered


def filter_by_date(articles: list, days_back: int = 7) -> list:
    """Keep articles published within the last `days_back` days.
    Articles with no known date are kept (benefit of the doubt)."""
    cutoff = datetime.now() - timedelta(days=days_back)
    filtered = [
        art for art in articles
        if art.pub_date is None or art.pub_date >= cutoff
    ]
    logger.info("Date filter: %d → %d articles", len(articles), len(filtered))
    return filtered


def _normalise(text: str) -> str:
    """Lowercase + remove punctuation/whitespace for comparison."""
    return re.sub(r"\W+", " ", text.lower()).strip()


def _similar(a: str, b: str, threshold: float = 0.85) -> bool:
    """Return True if two strings are very similar (above threshold)."""
    return SequenceMatcher(None, a, b).ratio() >= threshold


def deduplicate(articles: list) -> list:
    """
    Remove duplicates based on:
      1. Exact URL match
      2. Near-identical titles
      3. Near-identical body snippets (first 300 chars)
    """
    seen_urls: set = set()
    seen_titles: list = []
    seen_snippets: list = []
    unique = []

    for art in articles:
        # 1. URL dedupe
        if art.url in seen_urls:
            logger.debug("Duplicate URL: %s", art.url)
            continue

        # 2. Title dedupe
        norm_title = _normalise(art.title)
        if any(_similar(norm_title, t) for t in seen_titles):
            logger.debug("Duplicate title: %s", art.title)
            continue

        # 3. Body snippet dedupe
        body = getattr(art, "body", "")
        snippet = _normalise(body[:300])
        if snippet and any(_similar(snippet, s) for s in seen_snippets):
            logger.debug("Duplicate body snippet: %s", art.title)
            continue

        seen_urls.add(art.url)
        seen_titles.append(norm_title)
        if snippet:
            seen_snippets.append(snippet)
        unique.append(art)

    logger.info("Deduplicate: %d → %d articles", len(articles), len(unique))
    return unique


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


def clean_articles(articles: list) -> list:
    """Apply clean_text to each article's body in-place."""
    for art in articles:
        if hasattr(art, "body"):
            art.body = clean_text(art.body)
    return articles


def run_pipeline(articles: list, days_back: int = 7) -> list:
    """Run the full cleaning pipeline: date filter → keyword filter → dedup → clean."""
    articles = filter_by_date(articles, days_back)
    articles = filter_by_keywords(articles)
    articles = deduplicate(articles)
    articles = clean_articles(articles)
    logger.info("Cleaning pipeline complete. Final count: %d articles", len(articles))
    return articles
