# Source + Access Mode Architecture

## Status
Approved project architecture for the commercial Business-Scraper direction.

## Core model
Every scrape request identifies two independent dimensions:
Source + Access Mode

Examples:

ScrapeRequest(source="neshan", access_mode="web", ...)
ScrapeRequest(source="neshan", access_mode="api", api_key="...", ...)

## Target source matrix
Source
├── Google Maps
│   ├── Web
│   └── API
├── Neshan
│   ├── Web
│   └── API
└── Future Sources
    ├── Web
    └── API

The target is for each source to support Web and API when that source actually provides both access paths.

## Layering
Desktop / CLI / Web
        ↓
     Service
        ↓
 ScrapeRequest
        ↓
     Pipeline
        ↓
 Source Factory / Registry
        ↓
 Source Adapter
   ├── Web implementation
   └── API implementation
        ↓
 normalized Business
        ↓
 Cleaner / Deduplicator
        ↓
 Database / Export

The Core and Pipeline must not contain source-specific scraping logic.

## Desktop contract
The Desktop UI exposes:
- Source
- Access Mode
- API Key (enabled only for API mode)
- Keyword(s)
- Location
- Max Results

The selected Source + Access Mode are part of the scrape request.

## Determinism
There is no automatic Web/API fallback in the current architecture.
If the user selects API, an API failure remains an API failure.

## Traceability
ScrapeRun stores source and access_mode.
This allows run history, auditing, filtering and exports to distinguish how each run was executed.

## Incremental implementation policy
Do not rewrite working Google Maps scraping.

Implementation order:
1. Establish the Source + Access Mode contract.
2. Make Neshan support Web + API through the same contract.
3. Expose Source + Access Mode in Desktop.
4. Add Google Maps API adapter.
5. Apply the same adapter pattern to future sources.

Until an API adapter is implemented for a source, the UI/adapter must not pretend that API execution is supported.

## Current implementation status
- Google Maps Web: implemented.
- Google Maps API: planned next.
- Neshan Web: implementation in Phase 5.5.
- Neshan API: implemented as explicit API mode.
- Desktop Source + Access Mode selection: Phase 5.5.