# Google Maps API Adapter — Phase 5.6

## Status
Implemented in Phase 5.6 using Google Maps Platform Places API (New).

## Access contract
Google Maps now supports:
- Web → existing Playwright scraper
- API → Places API (New) Text Search

The public contract remains:
source="google_maps" + access_mode="web" | "api"

## API endpoint
Text Search (New):
POST https://places.googleapis.com/v1/places:searchText

Authentication:
- X-Goog-Api-Key
- API key is required only in API mode.

## Request
The adapter sends:
- textQuery: <keyword> <location>
- pageSize: up to 20 per API request
- pageToken: when additional pages are required.

The adapter caps API results at 30, matching the current source-level product limit.

## Field mask
The adapter requests only fields needed to populate the normalized Business model:
- place ID
- display name
- formatted address
- location
- national/international phone
- website
- rating
- user rating count
- primary type
- Google Maps URI

No wildcard field mask is used.

## Normalization
API Place data is mapped to the existing normalized Business dictionary.
The downstream Cleaner, Deduplicator, Pipeline, Database and Export layers remain unchanged.

## Failure behavior
- Missing API key → ValueError
- Non-2xx API response → GoogleMapsAPIError
- Invalid JSON → GoogleMapsAPIError
- API failure does not fall back to Web automatically.

## Desktop
When Source = Google Maps and Access Mode = API, the API key field is enabled.

## Security
API keys are runtime configuration. They are not stored in source code or embedded in the repository.

## Official API basis
This adapter targets Places API (New), the current Google Places web-service version. Text Search (New) uses HTTP POST and requires a response field mask.