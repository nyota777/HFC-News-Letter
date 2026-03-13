"""
deduplicator.py — Removing duplicate articles based on similarity.
"""

import re
from difflib import SequenceMatcher
from utils.logger import get_logger
from utils.models import Article

logger = get_logger(__name__)


def _normalise(text: str) -> str:
    """Lowercase + remove punctuation/whitespace for comparison."""
    if not text:
        return ""
    return re.sub(r"\W+", " ", text.lower()).strip()


def _similar(a: str, b: str, threshold: float = 0.85) -> bool:
    """Return True if two strings are very similar (above threshold)."""
    if not a or not b:
        return False
    return SequenceMatcher(None, a, b).ratio() >= threshold


def deduplicate(articles: list[Article]) -> list[Article]:
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
        snippet = _normalise(art.body[:300]) if art.body else ""
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
