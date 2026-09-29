# Business-Scraper

A modular, database-first business scraping engine with Google Maps as the current production source.

## Current scope

Version 1 is intentionally focused on **Google Maps end-to-end**.

The architecture is source-agnostic and prepared for future adapters, but additional sources are not part of the current implementation.

## Architecture

```text
CLI
 ↓
Application
 ↓
ScrapeRequest
 ↓
ScrapePipeline
 ↓
ScraperFactory / Registry
 ↓
GoogleMapsScraper
 ↓
BrowserManager
 ↓
Google Maps
 ↓
Cleaner
 ↓
Deduplicator
 ↓
SQLite / SQLAlchemy
 ↓
ExportService
 ↓
CSV / JSON / Excel
```

Core layers:

- Application / CLI
- Scraper
- Core
- Browser
- Database
- Export

## Features

- Google Maps scraping with Playwright
- Multi-keyword scraping
- Global deduplication
- Business cleaning and normalization
- SQLite persistence with SQLAlchemy
- ScrapeRun tracking
- ScrapeRun ↔ Business association
- Run history and inspection
- CSV, JSON, and Excel export
- Run-based export
- Professional Excel summary for run exports
- Retry and error isolation
- Browser lifecycle management
- Structured scrape results with run traceability
- Google Maps source ID extraction when the place URL exposes a stable identifier

## Requirements

- Python 3.12+
- Playwright
- SQLAlchemy
- openpyxl
- pytest

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## CLI

### Scrape Google Maps

```bash
python main.py scrape --location "مشهد" --keyword "فست فود" --max-results 30
```

Multiple keywords can be supplied:

```bash
python main.py scrape \
  --location "مشهد" \
  --keyword "فست فود" \
  --keyword "رستوران" \
  --max-results 50
```

### List scrape runs

```bash
python main.py runs
python main.py runs --limit 10
```

### Inspect a run

```bash
python main.py run 1
```

Show businesses associated with a run:

```bash
python main.py run 1 --businesses
```

### Export all businesses

```bash
python main.py export --format csv --output exports/businesses.csv
python main.py export --format json --output exports/businesses.json
python main.py export --format excel --output exports/businesses.xlsx
```

### Export a specific run

```bash
python main.py export --run-id 1 --format csv --output exports/run-1.csv
python main.py export --run-id 1 --format json --output exports/run-1.json
python main.py export --run-id 1 --format excel --output exports/run-1.xlsx
```

Run-based Excel exports include the business data plus a **Scrape Summary** sheet.

## Testing

Run the complete test suite:

```bash
pytest -q
```

The project is developed incrementally with regression tests covering the core pipeline, scraper, database, application, CLI, run history, associations, and exporters.

## Project structure

```text
app/
browser/
cli/
core/
database/
exporters/
logs/
scrapers/
tests/
config.py
main.py
requirements.txt
README.md
```

## Architectural principles

- Keep the core source-agnostic.
- Google Maps is the only implemented source in the current v1 scope.
- Future sources should be added through the scraper abstraction, registry, and factory rather than by coupling source-specific logic into the core.
- Keep the database as the durable source of scraped business data.
- Keep cleaning and deduplication outside source-specific extraction.
- Keep exporters independent from the scraping pipeline.
- Prefer small, testable changes over unnecessary abstractions.

## Current limitations

The following are intentionally outside the current v1 scope:

- GUI
- CRM / lead management
- AI enrichment
- additional scraping sources
- cloud database
- multi-user system
- CAPTCHA solving or access-control circumvention
- advanced proxy rotation

## Development workflow

Changes are developed in small feature branches and validated with the full test suite before merging into `main`.

The current implementation is designed to complete the Google Maps path first while keeping the architecture ready for future sources.
