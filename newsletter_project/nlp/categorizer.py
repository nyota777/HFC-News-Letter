"""
categorizer.py — Keyword-based article categorisation.
"""

import re
from utils.logger import get_logger
from utils.models import Article

logger = get_logger(__name__)

# Basic heuristics for categorising content
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
    "Global Financial Markets": [
        "federal reserve","fed","ecb","bank of england","global","international",
        "world","us bank","eu bank","wall street","london","new york",
        "emerging market","developing","interest rate hike","quantitative",
    ],
}

FALLBACK_CATEGORY = "General Finance"


def categorise(article: Article) -> str:
    """Return the best matching category for an article based on keyword counting."""
    text = f"{article.title} {article.body}".lower()
    scores = {}
    
    for category, keywords in CATEGORIES.items():
        # count occurrences of exact word boundaries
        score = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text))
        if score:
            scores[category] = score
            
    if scores:
        return max(scores, key=scores.get) # highest score wins
    return FALLBACK_CATEGORY


def categorise_articles(articles: list[Article]) -> list[Article]:
    """Add category to each article in-place."""
    for art in articles:
        art.category = categorise(art)
        logger.debug("Categorised '%s' → %s", art.title[:50], art.category)
    return articles
