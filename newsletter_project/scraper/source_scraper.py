"""
source_scraper.py — Scrapes article links from registered sources.
Handles retries, polite delays, and basic relevance checks.
"""

import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta

from config import USER_AGENTS, BAD_URL_FRAGMENTS, FINANCE_KEYWORDS, SOURCES, RSS_FEEDS, CUTOFF_DAYS
from utils.logger import get_logger
from utils.models import Article

logger = get_logger(__name__)

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }


def fetch_html(url: str, retries: int=3, delay: float=2.0) -> str | None:
    """Fetch raw HTML for a URL with robust retry and backoff logic."""
    for attempt in range(retries):
        try:
            time.sleep(delay + random.uniform(0.3, 1.0))
            resp = requests.get(url, headers=get_headers(), timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            logger.warning(f"HTTP {status} on {url} (attempt {attempt+1}/{retries})")
            if status in (403, 429, 503):
                time.sleep(delay * (attempt + 2)) # backoff
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed: {e} (attempt {attempt+1}/{retries})")
            time.sleep(delay * (attempt + 1))
    return None


def is_finance_relevant(text: str) -> bool:
    """Check if the title/text contains at least one finance keyword."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in FINANCE_KEYWORDS)


def scrape_html_links(source_name: str, base_url: str) -> list[Article]:
    """Extract article links directly from HTML pages."""
    html = fetch_html(base_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen_links = set()
    
    for a_tag in soup.find_all("a", href=True):
        title = a_tag.get_text(separator=" ", strip=True)
        href = a_tag["href"].strip()
        
        # Validation checks
        if len(title) < 25 or len(title) > 300:
            continue
        if any(bad in href.lower() for bad in BAD_URL_FRAGMENTS):
            continue
            
        # Normalize URLs
        if href.startswith("/"):
            href = urljoin(base_url, href)
        elif not href.startswith("http"):
            continue
            
        if urlparse(href).netloc != urlparse(base_url).netloc:
            continue
        if href in seen_links:
            continue
            
        seen_links.add(href)
        
        if not is_finance_relevant(title):
            continue
            
        art = Article(title=title, url=href, source=source_name)
        results.append(art)
        
        if len(results) >= 15: # limits per source scraping to top 15 matches to avoid overload
            break
            
    logger.info(f"[HTML] {source_name}: {len(results)} links found")
    return results


def scrape_rss_links(source_name: str, feed_url: str, cutoff_days: int = CUTOFF_DAYS) -> list[Article]:
    """Extract article links and dates from RSS feeds."""
    html = fetch_html(feed_url, delay=1.0)
    if not html:
        return []
        
    try:
        soup = BeautifulSoup(html, "lxml-xml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
        
    items = soup.find_all("item") or soup.find_all("entry")
    cutoff = datetime.now() - timedelta(days=cutoff_days)
    results = []
    
    for item in items[:20]: # Parse up to 20 top entries
        title_tag = item.find("title")
        link_tag  = item.find("link") or item.find("guid")
        date_tag  = item.find("pubDate") or item.find("published") or item.find("updated")
        
        if not title_tag or not link_tag:
            continue
            
        title = title_tag.get_text(strip=True)
        link  = link_tag.get_text(strip=True) if link_tag.string else link_tag.get("href", "")
        
        if not link or not link.startswith("http") or len(title) < 15:
            continue
            
        pub_date: datetime | None = None
        if date_tag:
            raw = date_tag.get_text(strip=True)
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
                try:
                    parsed_date = datetime.strptime(raw[:30], fmt)
                    # remove timezone info for uniform calculation
                    pub_date = parsed_date.replace(tzinfo=None) if parsed_date.tzinfo else parsed_date
                    break
                except ValueError:
                    continue
                    
        # Filter purely by cutoff here if the date is successfully grabbed
        if pub_date and pub_date < cutoff:
            continue
            
        art = Article(title=title, url=link, source=source_name, pub_date=pub_date)
        results.append(art)
        
    logger.info(f"[RSS] {source_name}: {len(results)} links found")
    return results

def scrape_all_sources(days_back: int = CUTOFF_DAYS) -> list[Article]:
    """Execute scraping across all configured HTML and RSS targets."""
    logger.info(f"Starting scraping logic. Lookback days = {days_back}")
    articles = []

    # Scrape RSS feeds first
    for source_name, feed_url in RSS_FEEDS.items():
        arts = scrape_rss_links(source_name, feed_url, cutoff_days=days_back)
        articles.extend(arts)

    # Scrape raw HTML for sites without a defined RSS
    for source_name, base_url in SOURCES.items():
        if source_name not in RSS_FEEDS:
            arts = scrape_html_links(source_name, base_url)
            articles.extend(arts)

    logger.info(f"Total articles discovered via scraping: {len(articles)}")
    return articles
