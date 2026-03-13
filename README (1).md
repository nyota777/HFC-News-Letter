# HFC Weekly Financial Intelligence Newsletter

Automated Python pipeline that scrapes, filters, summarises, and formats a weekly newsletter for HFC Group Plc.

## Project Structure

```
hfc_newsletter/
├── main.py                    # Orchestrator — run this
├── scraper.py                 # Scrape article links & metadata
├── article_parser.py          # Extract full article body text
├── cleaner.py                 # Clean, filter by date/keyword, deduplicate
├── summarizer.py              # Extractive summarisation + key takeaways
├── categorizer.py             # Keyword-based article categorisation
├── newsletter_generator.py    # Render TXT, HTML, CSV outputs
├── HFC_Newsletter_Colab.ipynb # Google Colab version (self-contained)
├── requirements.txt
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py --days 7 --output output/
```

## Google Colab
Open `HFC_Newsletter_Colab.ipynb` in Google Colab and run all cells.

## Automation
See the automation section in the Colab notebook for GitHub Actions, cron, and Windows Task Scheduler examples.
