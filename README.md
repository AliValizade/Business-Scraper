# Business-Scraper

A modular, database-first business scraping platform with Google Maps and Neshan as the current production sources, plus a PySide6 desktop interface for running and inspecting scrape jobs.

## Current scope

The current product supports **Google Maps and Neshan** through a source + access mode architecture.

Each implemented source can expose Web and API access independently.

## Architecture

```text
Desktop GUI / CLI
 ↓
Application
 ↓
ScrapeRequest
 ↓
ScrapePipeline
 ↓
ScraperFactory / Registry
 ↓
Source Adapter
 ↓
Web / API Access
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

- Google Maps and Neshan scraping
- Web and API access modes per source
- Multi-keyword scraping
- Global deduplication
- Business cleaning and normalization
- SQLite persistence with SQLAlchemy
- ScrapeRun tracking
- ScrapeRun ↔ Business association
- Run history and inspection
- CSV, JSON, and Excel export
- Run-based export
- PySide6 desktop dashboard with collapsible navigation
- Scrape, run history, results, settings, and license pages
- Light/dark desktop themes
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

## Desktop application

Launch the desktop dashboard:

```bash
python desktop.py
```

The desktop interface provides source/access-mode selection, scrape controls, progress feedback, run history, run results, and CSV/JSON/Excel export.

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
interfaces/
services/
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
- Google Maps and Neshan are implemented sources; each source is selected independently from its Web/API access mode.
- Future sources should be added through the scraper abstraction, registry, and factory rather than by coupling source-specific logic into the core.
- Keep the database as the durable source of scraped business data.
- Keep cleaning and deduplication outside source-specific extraction.
- Keep exporters independent from the scraping pipeline.
- Prefer small, testable changes over unnecessary abstractions.

## Current limitations

The following are intentionally outside the current v1 scope:

- CRM / lead management
- AI enrichment
- additional scraping sources beyond the current Google Maps and Neshan adapters
- cloud database
- multi-user system
- CAPTCHA solving or access-control circumvention
- advanced proxy rotation

## Development workflow

Changes are developed in small feature branches and validated with the full test suite before merging into `main`.

The current implementation is designed to complete the Google Maps path first while keeping the architecture ready for future sources.
