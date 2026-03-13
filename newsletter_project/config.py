"""
config.py — Configuration settings for the HFC Newsletter Pipeline.
"""

# Number of days to look back for articles
CUTOFF_DAYS = 7

# Sources to scrape from (Name -> URL)
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
    "BBC Business":          "https://www.bbc.com/business",
    "Kenya Moja Business":   "https://www.kenyamoja.com/business",
    "Capital FM Business":   "https://www.capitalfm.co.ke/business/",
    "ePaper Nation Africa":  "https://epaper.nation.africa/product/business-daily",
    "People Daily Business": "https://peopledaily.digital/business",
    "CNN Business":          "https://edition.cnn.com/business",
    "FT Markets":            "https://www.ft.com/markets"
}

# RSS feeds
RSS_FEEDS = {
    "Business Daily Africa": "https://www.businessdailyafrica.com/bd/markets/rss",
    "Daily Nation":           "https://nation.africa/kenya/business/rss",
    "Standard Media":         "https://www.standardmedia.co.ke/rss/business.xml",
    "The Star Kenya":         "https://www.the-star.co.ke/business/rss",
    "Kenyan Wall Street":     "https://kenyanwallstreet.com/feed/",
    "Reuters Finance":        "https://feeds.reuters.com/reuters/businessNews",
}

# Keywords to determine if an article is finance-relevant
FINANCE_KEYWORDS = [
    "bank", "banking", "mortgage", "interest rate", "loan", "inflation",
    "credit", "central bank", "fintech", "housing finance", "regulation",
    "investment", "economy", "economic", "financial", "finance", "equity",
    "bonds", "forex", "exchange rate", "kra", "tax", "treasury", "cbk",
    "kcb", "equity bank", "cooperative bank", "stanbic", "absa", "ncba",
    "hfc", "dtb", "premier bank", "fund", "capital market", "nse",
    "imf", "world bank", "gdp", "monetary policy", "fiscal", "insurance",
]

# Order of categories in the final newsletter
CATEGORY_ORDER = [
    "Kenyan Banking News",
    "Economic Updates",
    "Regulatory & Policy Changes",
    "Fintech & Technology",
    "Global Financial Markets",
    "General Finance",
]

# URL fragments to ignore during scraping
BAD_URL_FRAGMENTS = [
    "twitter.com", "facebook.com", "linkedin.com", "instagram.com",
    "youtube.com", "login", "register", "/author/", "/tag/", "/page/",
    "mailto:", "javascript:", "#", "whatsapp", "telegram",
    "subscribe", "newsletter", "advertise", "contact", "about",
]

# User agents for cycling
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
]
