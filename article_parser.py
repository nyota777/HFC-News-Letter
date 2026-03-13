"""
article_parser.py — Extract full article body text from URLs.

Uses newspaper3k as primary extractor; falls back to BeautifulSoup heuristics
when newspaper3k fails or returns too little text.
"""

import logging
import time
import random
import requests
from bs4 import BeautifulSoup
from typing import Optional

logger = logging.getLogger(__name__)

# Try importing newspaper3k (optional but preferred)
try:
    from newspaper import Article as NewspaperArticle
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    logger.warning("newspaper3k not installed — falling back to BeautifulSoup parser.")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

MIN_BODY_LENGTH = 150  # characters — below this we consider extraction failed


def _fetch_html(url: str) -> Optional[str]:
    """Fetch raw HTML for a URL with basic retry."""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            logger.warning("Fetch attempt %d failed for %s: %s", attempt + 1, url, exc)
            time.sleep((2 ** attempt) + random.uniform(0, 0.5))
    return None


def _extract_with_newspaper(url: str) -> Optional[str]:
    """Use newspaper3k to extract article text."""
    if not NEWSPAPER_AVAILABLE:
        return None
    try:
        art = NewspaperArticle(url)
        art.download()
        art.parse()
        text = art.text.strip()
        return text if len(text) >= MIN_BODY_LENGTH else None
    except Exception as exc:
        logger.debug("newspaper3k failed for %s: %s", url, exc)
        return None


def _extract_with_bs4(html: str) -> Optional[str]:
    """
    Fallback: extract article text using BeautifulSoup heuristics.
    Targets common content containers and removes boilerplate.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "button", "iframe", "noscript"]):
        tag.decompose()

    # Try common article container selectors in priority order
    candidates = [
        "article", "[itemprop='articleBody']", ".article-body",
        ".post-content", ".entry-content", ".story-body",
        ".content-body", "main", ".main-content",
    ]
    for selector in candidates:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(separator=" ", strip=True)
            if len(text) >= MIN_BODY_LENGTH:
                return text

    # Last resort: longest <div> with substantial text
    divs = soup.find_all("div")
    if divs:
        best = max(divs, key=lambda d: len(d.get_text(strip=True)))
        text = best.get_text(separator=" ", strip=True)
        if len(text) >= MIN_BODY_LENGTH:
            return text

    return None


def parse_article(url: str) -> Optional[str]:
    """
    Extract the main body text from an article URL.
    Returns cleaned text string or None if extraction fails.
    """
    # 1. Try newspaper3k (best quality)
    text = _extract_with_newspaper(url)
    if text:
        logger.debug("Parsed via newspaper3k: %s", url)
        return text

    # 2. Fall back to BS4 heuristics
    html = _fetch_html(url)
    if html:
        text = _extract_with_bs4(html)
        if text:
            logger.debug("Parsed via BeautifulSoup fallback: %s", url)
            return text

    logger.warning("Could not extract body text from %s", url)
    return None


def parse_articles_batch(articles: list, throttle: float = 1.0) -> list:
    """
    Parse body text for a list of ArticleMetadata objects in-place.
    Adds a `body` attribute to each object. Returns the updated list.
    """
    for i, art in enumerate(articles):
        logger.info("Parsing article %d/%d: %s", i + 1, len(articles), art.url)
        body = parse_article(art.url)
        art.body = body or ""
        time.sleep(throttle + random.uniform(0, 0.5))
    return articles
