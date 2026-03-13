"""
categorizer.py — Keyword-based article categorisation.
"""

import re
import logging

logger = logging.getLogger(__name__)

CATEGORIES = {
    "Kenyan Banking News": [
        "kenya","kenyan","nairobi","kcb","equity bank","cooperative bank",
        "hfc","housing finance","absa","stanbic","i&m","dtb","family bank",
        "ncba","standard chartered kenya","cbk","central bank of kenya",
    ],
    "Economic Updates": [
        "gdp","inflation","economy","economic","growth","recession","employment",
        "unemployment","trade","exports","imports","budget","fiscal","deficit",
        "surplus","revenue","tax","taxation","monetary policy",
    ],
    "Regulatory & Policy Changes": [
        "regulation","policy","law","legislation","compliance","regulator",
        "central bank","imf","world bank","directive","guideline","circular",
        "amendment","statutory","approval","license","licensing",
    ],
    "Fintech & Technology": [
        "fintech","mobile money","mpesa","m-pesa","digital","blockchain",
        "cryptocurrency","crypto","payment","wallet","app","technology",
        "innovation","startup","api","open banking","neobank",
    ],
    "Global Banking Trends": [
        "federal reserve","fed","ecb","bank of england","global","international",
        "world","us bank","eu bank","wall street","london","new york",
        "emerging market","developing","interest rate hike","quantitative",
    ],
}

FALLBACK_CATEGORY = "General Finance"


def categorise(article) -> str:
    """Return the best matching category for an article."""
    text = f"{article.title} {getattr(article, 'body', '')}".lower()
    scores = {}
    for category, keywords in CATEGORIES.items():
        score = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text))
        if score:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return FALLBACK_CATEGORY


def categorise_articles(articles: list) -> list:
    """Add `category` attribute to each article in-place."""
    for art in articles:
        art.category = categorise(art)
        logger.debug("Categorised '%s' → %s", art.title[:50], art.category)
    return articles
