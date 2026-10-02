# Phase 5.1 — Neshan Source Specification

## Status

**Phase:** 5.1
**Source:** Neshan
**Source key:** `neshan`
**Status:** Specification complete; implementation blocked only on a valid Neshan API key/service activation for real integration testing.

## 1. Goal

Add Neshan as the second independent business-data source without changing the existing Google Maps scraper or source-agnostic Core.

The target architecture remains:

```text
ScrapeRequest
    ↓
ScrapePipeline
    ↓
ScraperFactory
    ↓
ScraperRegistry
    ├── google_maps → GoogleMapsScraper
    └── neshan     → NeshanScraper
```

## 2. Official Neshan API contract

Neshan currently documents:

- Search API: `GET https://api.neshan.org/v3/search`
- POI Details API: `GET https://api.neshan.org/v1/point`
- Geocoding API: `GET https://api.neshan.org/geocoding/v1`

All require an `Api-Key` header.

Search API:
- accepts `q` as URL-encoded JSON;
- `q.term` is the search text;
- `q.center.latitude` and `q.center.longitude` are required;
- returns at most 30 relevant results per request;
- returns `title`, `address`, `category`, `type`, `region`, `neighbourhood`, `location`, and optionally `poiHash`.

POI Details:
- accepts `hash` as the POI identifier;
- returns `name`, `address`, `phoneNumber`, `website`, `workHours`, `layer`, `location`, and `socialNetworks`;
- `poiHash` exists only for verified Neshan places, so not every search result can be enriched.

Geocoding:
- converts the existing project `location` string into coordinates;
- accepts address/city/province and optional center/extent;
- can return multiple candidate coordinates.

## 3. Required authentication

Neshan API access is credential-based.

The implementation must NOT hard-code an API key.

Planned configuration:

```text
NESHHAN_API_KEY
```

Canonical environment variable:

```text
NESHHAN_API_KEY
```

> Note: the canonical name must be finalized in Phase 5.2 before implementation; no key name is committed by this phase.

The source adapter should fail clearly when the key is missing rather than attempting browser scraping or undocumented endpoints.

## 4. Search flow

For a normal project request:

```text
location string
    ↓
Neshan Geocoding
    ↓
center latitude/longitude
    ↓
Neshan Search API
    ↓
up to 30 result items
    ↓
optional POI Details enrichment
    ↓
normalized business dictionaries
    ↓
existing Cleaner
    ↓
existing Deduplicator
    ↓
existing Database/Pipeline
```

The adapter should preserve the current `BaseScraper.search(query, location)` contract.

The adapter may perform geocoding internally because the current common request model represents location as text.

## 5. Result mapping

### Search-level mapping

| Neshan | Business |
|---|---|
| `title` | `name` |
| `category` / `type` | `category` |
| `address` | `address` |
| request location / resolved city | `city` |
| `location.y` | `latitude` |
| `location.x` | `longitude` |
| `poiHash` | `source_id` |

### POI Details mapping

| Neshan | Business |
|---|---|
| `name` | `name` |
| `address` | `address` |
| `phoneNumber` | `phone` |
| `website` | `website` |
| `location.y` | `latitude` |
| `location.x` | `longitude` |
| `layer.title` | `category` |
| `socialNetworks` | optional `instagram` extraction only when the returned data explicitly identifies Instagram |

Fields not documented by Neshan are not fabricated:

- `rating` → None
- `reviews_count` → None
- `google_maps_url` → None

`source` must be:

```text
neshan
```

`source_id` should use `poiHash` when available. Results without `poiHash` remain valid search results, but cannot use POI Details enrichment.

## 6. Enrichment policy

Phase 5.2 should use a conservative enrichment strategy:

1. Search all matching results.
2. Keep every valid search result.
3. Call POI Details only when `poiHash` exists.
4. If POI Details fails for one result, keep the search-level record and increment/log the source-level error rather than discarding the business.
5. Never let one POI enrichment failure abort the complete scrape.

This preserves the existing pipeline's error-isolation philosophy.

## 7. Pagination / result limit

The documented Search API returns a maximum of 30 relevant results per request.

Phase 5.1 does **not** assume undocumented pagination.

Therefore:

- `max_results <= 30`: return up to `max_results`.
- `max_results > 30`: the initial implementation must not pretend that more than 30 results were retrieved.
- If Neshan later documents a supported pagination/tiling mechanism, it can be added as a separate phase.

## 8. Browser dependency

Neshan's official API is the primary integration path.

The Neshan adapter should therefore not depend on Playwright for API access.

The existing `BaseScraper` currently requires `browser_manager`; Phase 5.2 must resolve this architectural mismatch with the smallest compatible change.

Preferred direction:

- preserve the existing Google Maps constructor unchanged;
- allow API-based source adapters to operate without browser automation;
- do not make Core/Pipeline aware of Neshan-specific behavior.

## 9. Error handling

The adapter must recognize at least:

- 400 — invalid arguments
- 470 — invalid coordinates
- 480 — missing/invalid API key
- 481 — usage limit exceeded
- 482 — rate exceeded
- 483 — API key type mismatch
- 484 — API whitelist error
- 485 — service not enabled for key
- 500 — generic service error
- 404 — invalid endpoint

HTTP failures must be converted into source-level scraper errors consistent with the existing retry/error-isolation conventions.

Retry behavior must be conservative for authentication/configuration errors; those should not be blindly retried.

## 10. Data integrity

The existing Core remains responsible for:

```text
Cleaner
Deduplicator
Database
ScrapeRun
ScrapeResult
```

Neshan-specific code should only:

```text
resolve location
→ call Neshan APIs
→ map response
→ return raw/normalized business dictionaries
```

No Neshan-specific database model is required by Phase 5.1.

## 11. Tests required in Phase 5.2

Unit tests:

- missing API key
- request construction
- URL encoding of Persian search text
- geocoding response parsing
- Search response parsing
- POI Details response parsing
- coordinate mapping (`x=longitude`, `y=latitude`)
- missing `poiHash`
- partial POI enrichment failure
- API error mapping
- result limit behavior
- BaseScraper/source contract

Integration tests:

- registry contains `neshan`
- factory creates `NeshanScraper`
- pipeline accepts source=`neshan`
- Google Maps tests remain unchanged
- full pipeline normalization/deduplication remains source-agnostic

Real API test:

- requires a valid Neshan API key with Search API and POI Details API enabled;
- test location: a known Iranian city;
- test keyword: a common business category;
- verify returned records and field mapping.

## 12. Explicit non-goals

Phase 5.1/5.2 will not:

- scrape undocumented/private Neshan endpoints;
- bypass authentication, rate limits, CAPTCHA, or access controls;
- reverse-engineer private mobile APIs;
- modify Google Maps behavior;
- add a Neshan-specific database schema;
- claim more than the documented 30 Search API results without a documented mechanism.

## 13. Phase boundary

### Phase 5.1 — Complete

- source feasibility research
- official API identification
- authentication requirements
- data contract
- field mapping
- location-resolution strategy
- error contract
- test contract
- implementation blockers identified

### Phase 5.2 — Next

Implement `NeshanScraper` and the minimal infrastructure required for API-based sources, then add unit/contract tests.

### Phase 5.3 — Next

Register Neshan in the default registry and validate the complete pipeline with a real API key.

### Phase 5.4 — Next

Desktop source selection/configuration and packaged application validation, if required after CLI/core validation.
