"""
main.py — Orchestrator: run the full HFC newsletter pipeline.

Usage:
    python main.py [--days 7] [--output output/]
"""

import argparse
from datetime import datetime

from config import CUTOFF_DAYS
from scraper.source_scraper import scrape_all_sources
from scraper.article_extractor import parse_articles_batch
from processing.cleaner import run_pipeline
from nlp.summarizer import summarise_articles
from nlp.categorizer import categorise_articles
from output.newsletter_generator import generate_newsletter
from utils.logger import get_logger

logger = get_logger("main")


def run(days_back: int = CUTOFF_DAYS, output_dir: str = "output") -> None:
    logger.info("━━━━━━━━ HFC Newsletter Pipeline START ━━━━━━━━")
    start = datetime.now()

    # 1. Scrape
    logger.info("Step 1/5 — Scraping sources …")
    articles = scrape_all_sources(days_back=days_back)
    if not articles:
        logger.warning("No articles scraped. Exiting.")
        return

    # 2. Extract article bodies
    logger.info("Step 2/5 — Extracting article bodies …")
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
    logger.info("Outputs generated:")
    for ext, path in paths.items():
        logger.info("  [%s] %s", ext.upper(), path)

    print(f"\n[SUCCESS] Newsletter generated! {len(articles)} articles across {len(paths)} formats.")
    print(f"   DOCX → {paths['docx']}")
    print(f"   HTML → {paths['html']}")
    print(f"   MD   → {paths['md']}")
    print(f"   TXT  → {paths['txt']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HFC Weekly Newsletter Generator")
    parser.add_argument("--days",   type=int, default=CUTOFF_DAYS, help="Look-back window in days")
    parser.add_argument("--output", type=str, default="output",    help="Output directory")
    args = parser.parse_args()
    run(days_back=args.days, output_dir=args.output)
