"""
main.py — Orchestrator: run the full HFC newsletter pipeline.

Usage:
    python main.py [--days 7] [--output output/]
"""

import argparse
import logging
import sys
from datetime import datetime

from scraper import scrape_all_sources
from article_parser import parse_articles_batch
from cleaner import run_pipeline
from summarizer import summarise_articles
from categorizer import categorise_articles
from newsletter_generator import generate_newsletter

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("hfc_pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


def run(days_back: int = 7, output_dir: str = "output") -> None:
    logger.info("━━━━━━━━ HFC Newsletter Pipeline START ━━━━━━━━")
    start = datetime.now()

    # 1. Scrape
    logger.info("Step 1/5 — Scraping sources …")
    articles = scrape_all_sources(days_back=days_back)
    if not articles:
        logger.warning("No articles scraped. Exiting.")
        return

    # 2. Parse article bodies
    logger.info("Step 2/5 — Parsing article bodies …")
    articles = parse_articles_batch(articles, throttle=1.0)

    # 3. Clean & filter
    logger.info("Step 3/5 — Cleaning & filtering …")
    articles = run_pipeline(articles, days_back=days_back)
    if not articles:
        logger.warning("No articles remaining after cleaning. Exiting.")
        return

    # 4. Summarise
    logger.info("Step 4/5 — Summarising …")
    articles = summarise_articles(articles)

    # 5. Categorise & generate newsletter
    logger.info("Step 5/5 — Categorising & generating newsletter …")
    articles = categorise_articles(articles)
    paths = generate_newsletter(articles, output_dir=output_dir)

    elapsed = (datetime.now() - start).total_seconds()
    logger.info("━━━━━━━━ Pipeline complete in %.1fs ━━━━━━━━", elapsed)
    logger.info("Outputs:")
    for fmt, path in paths.items():
        logger.info("  [%s] %s", fmt.upper(), path)

    print(f"\n✅ Newsletter generated! {len(articles)} articles across {len(paths)} formats.")
    print(f"   HTML → {paths['html']}")
    print(f"   TXT  → {paths['txt']}")
    print(f"   CSV  → {paths['csv']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HFC Weekly Newsletter Generator")
    parser.add_argument("--days",   type=int, default=7,        help="Look-back window in days")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    args = parser.parse_args()
    run(days_back=args.days, output_dir=args.output)
