"""
newsletter_generator.py — Produce the final formatted newsletter.

Outputs:
  • Plain-text  (.txt)
  • HTML        (.html)
  • CSV backup  (.csv)
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

CATEGORY_ORDER = [
    "Kenyan Banking News",
    "Economic Updates",
    "Regulatory & Policy Changes",
    "Fintech & Technology",
    "Global Banking Trends",
    "General Finance",
]


def _group_by_category(articles: list) -> dict:
    groups = defaultdict(list)
    for art in articles:
        groups[getattr(art, "category", "General Finance")].append(art)
    return groups


# ── Plain-text renderer ───────────────────────────────────────────────────────
def render_text(articles: list, week_ending: str = None) -> str:
    if week_ending is None:
        week_ending = datetime.now().strftime("%d %B %Y")

    lines = [
        "=" * 65,
        "  HFC WEEKLY FINANCIAL INTELLIGENCE NEWSLETTER",
        f"  Week Ending: {week_ending}",
        "=" * 65,
        "",
    ]

    groups = _group_by_category(articles)

    for category in CATEGORY_ORDER:
        arts = groups.get(category, [])
        if not arts:
            continue
        lines += [
            f"{'─' * 65}",
            f"  {category.upper()}",
            f"{'─' * 65}",
            "",
        ]
        for art in arts:
            pub = art.pub_date.strftime("%d %b %Y") if art.pub_date else "Date unknown"
            summary = getattr(art, "summary", "")
            takeaway = getattr(art, "takeaway", "")
            lines += [
                f"• {art.title}",
                f"  Source: {art.source}  |  {pub}",
                f"  {summary}" if summary else "",
                f"  ➤ Key Takeaway: {takeaway}" if takeaway else "",
                f"  🔗 {art.url}",
                "",
            ]

    lines += [
        "=" * 65,
        "  HFC Group Plc — Internal Distribution Only",
        f"  Generated: {datetime.now().strftime('%d %B %Y %H:%M')}",
        "=" * 65,
    ]
    return "\n".join(lines)


# ── HTML renderer ─────────────────────────────────────────────────────────────
def render_html(articles: list, week_ending: str = None) -> str:
    if week_ending is None:
        week_ending = datetime.now().strftime("%d %B %Y")

    groups = _group_by_category(articles)

    section_html = ""
    for category in CATEGORY_ORDER:
        arts = groups.get(category, [])
        if not arts:
            continue
        items_html = ""
        for art in arts:
            pub = art.pub_date.strftime("%d %b %Y") if art.pub_date else "Date unknown"
            summary = getattr(art, "summary", "")
            takeaway = getattr(art, "takeaway", "")
            items_html += f"""
            <div class="article">
              <h3><a href="{art.url}" target="_blank">{art.title}</a></h3>
              <p class="meta">{art.source} &nbsp;|&nbsp; {pub}</p>
              <p class="summary">{summary}</p>
              <p class="takeaway"><strong>Key Takeaway:</strong> {takeaway}</p>
            </div>"""
        section_html += f"""
        <section>
          <h2>{category}</h2>
          {items_html}
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HFC Weekly Newsletter — {week_ending}</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #222; }}
  header {{ background: #003366; color: white; padding: 24px; border-radius: 4px; margin-bottom: 24px; }}
  header h1 {{ margin: 0; font-size: 1.6em; }}
  header p {{ margin: 4px 0 0; opacity: .8; }}
  section {{ margin-bottom: 32px; }}
  h2 {{ background: #e8f0fe; padding: 8px 14px; border-left: 4px solid #003366; font-size: 1.1em; }}
  .article {{ border-bottom: 1px solid #eee; padding: 12px 0; }}
  .article h3 {{ margin: 0 0 4px; font-size: 1em; }}
  .article h3 a {{ color: #003366; text-decoration: none; }}
  .meta {{ font-size: .8em; color: #777; margin: 0 0 6px; }}
  .summary {{ margin: 0 0 4px; }}
  .takeaway {{ font-size: .9em; background: #fffbe6; padding: 6px 10px; border-radius: 3px; }}
  footer {{ font-size: .8em; color: #888; border-top: 1px solid #ddd; padding-top: 12px; margin-top: 32px; }}
</style>
</head>
<body>
<header>
  <h1>HFC Weekly Financial Intelligence Newsletter</h1>
  <p>Week Ending: {week_ending}</p>
</header>
{section_html}
<footer>HFC Group Plc — Internal Distribution Only &nbsp;|&nbsp;
Generated: {datetime.now().strftime("%d %B %Y %H:%M")}</footer>
</body>
</html>"""


# ── CSV export ────────────────────────────────────────────────────────────────
def export_csv(articles: list, path: str) -> None:
    fields = ["title", "source", "pub_date", "category", "url", "summary", "takeaway"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for art in articles:
            writer.writerow({
                "title": art.title,
                "source": art.source,
                "pub_date": art.pub_date.strftime("%Y-%m-%d") if art.pub_date else "",
                "category": getattr(art, "category", ""),
                "url": art.url,
                "summary": getattr(art, "summary", ""),
                "takeaway": getattr(art, "takeaway", ""),
            })
    logger.info("CSV exported to %s", path)


def generate_newsletter(articles: list, output_dir: str = "output") -> dict:
    """
    Run all renderers, write files, return dict of output paths.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    txt_path  = f"{output_dir}/hfc_newsletter_{date_str}.txt"
    html_path = f"{output_dir}/hfc_newsletter_{date_str}.html"
    csv_path  = f"{output_dir}/hfc_newsletter_{date_str}.csv"

    week_ending = datetime.now().strftime("%d %B %Y")

    txt_content  = render_text(articles, week_ending)
    html_content = render_html(articles, week_ending)

    with open(txt_path,  "w", encoding="utf-8") as f:
        f.write(txt_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    export_csv(articles, csv_path)

    logger.info("Newsletter saved → %s, %s, %s", txt_path, html_path, csv_path)
    return {"txt": txt_path, "html": html_path, "csv": csv_path}
