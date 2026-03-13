"""
scraper.py — Article link scraper with retry logic, headers, and throttling.
"""
import requests
import logging
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

CUTOFF_DAYS = 7

SOURCES = {
    "Central Bank of Kenya": "https://www.centralbank.go.ke/press-releases/",
    "Business Daily Africa": "https://www.businessdailyafrica.com/bd/markets",
    "Kenyan Wall Street":    "https://kenyanwallstreet.com/category/banking/",
    "Daily Nation":          "https://nation.africa/kenya/business",
    "Reuters Finance":       "https://www.reuters.com/business/finance/",
    "Business Today Kenya":  "https://businesstoday.co.ke/",
    "The Star Kenya":        "https://www.the-star.co.ke/business/",
    "Standard Media":        "https://www.standardmedia.co.ke/business",
    "Kenyans.co.ke":         "https://www.kenyans.co.ke/business",
    "Finance in Africa":     "https://financeinafrica.com/",
}

RSS_FEEDS = {
    "Business Daily Africa": "https://www.businessdailyafrica.com/bd/markets/rss",
    "Daily Nation":           "https://nation.africa/kenya/business/rss",
    "Standard Media":         "https://www.standardmedia.co.ke/rss/business.xml",
    "The Star Kenya":         "https://www.the-star.co.ke/business/rss",
    "Kenyan Wall Street":     "https://kenyanwallstreet.com/feed/",
    "Reuters Finance":        "https://feeds.reuters.com/reuters/businessNews",
}

FINANCE_KEYWORDS = [
    "bank", "banking", "mortgage", "interest rate", "loan", "inflation",
    "credit", "central bank", "fintech", "housing finance", "regulation",
    "investment", "economy", "economic", "financial", "finance", "equity",
    "bonds", "forex", "exchange rate", "kra", "tax", "treasury", "cbk",
    "kcb", "equity bank", "cooperative bank", "stanbic", "absa", "ncba",
    "hfc", "dtb", "premier bank", "fund", "capital market", "nse",
    "imf", "world bank", "gdp", "monetary policy", "fiscal", "insurance",
]

BAD_URL_FRAGMENTS = [
    "twitter.com", "facebook.com", "linkedin.com", "instagram.com",
    "youtube.com", "login", "register", "/author/", "/tag/", "/page/",
    "mailto:", "javascript:", "#", "whatsapp", "telegram",
    "subscribe", "newsletter", "advertise", "contact", "about",
]


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }


def fetch_html(url, retries=3, delay=2.0):
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
                time.sleep(delay * (attempt + 2))
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed: {e} (attempt {attempt+1}/{retries})")
            time.sleep(delay * (attempt + 1))
    return None


def is_finance_relevant(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in FINANCE_KEYWORDS)


def scrape_html_links(source_name, base_url):
    html = fetch_html(base_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen_links = set()
    for a_tag in soup.find_all("a", href=True):
        title = a_tag.get_text(separator=" ", strip=True)
        href = a_tag["href"].strip()
        if len(title) < 25 or len(title) > 300:
            continue
        if any(bad in href.lower() for bad in BAD_URL_FRAGMENTS):
            continue
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
        results.append({"title": title, "link": href, "source": source_name})
        if len(results) >= 15:
            break
    logger.info(f"[HTML] {source_name}: {len(results)} links")
    return results


def scrape_rss_links(source_name, feed_url, cutoff_days=CUTOFF_DAYS):
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
    for item in items[:20]:
        title_tag = item.find("title")
        link_tag  = item.find("link") or item.find("guid")
        date_tag  = item.find("pubDate") or item.find("published") or item.find("updated")
        if not title_tag or not link_tag:
            continue
        title = title_tag.get_text(strip=True)
        link  = link_tag.get_text(strip=True) if link_tag.string else link_tag.get("href", "")
        if not link or not link.startswith("http") or len(title) < 15:
            continue
        pub_date = None
        if date_tag:
            raw = date_tag.get_text(strip=True)
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
                try:
                    pub_date = datetime.strptime(raw[:30], fmt)
                    if pub_date.tzinfo:
                        pub_date = pub_date.replace(tzinfo=None)
                    break
                except ValueError:
                    continue
        if pub_date and pub_date < cutoff:
            continue
        results.append({"title": title, "link": link, "source": source_name, "pub_date": pub_date})
    logger.info(f"[RSS] {source_name}: {len(results)} links")
    return results
