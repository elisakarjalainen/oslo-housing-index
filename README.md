# oslo-housing-index

Tracks rental price developments across Oslo neighbourhoods over time.

This tool collects listing-level data from finn.no (postal code, price, size, property type, bedrooms, agency vs. private) and stores it as timestamped JSON snapshots. The goal is to build a price index that enables comparisons between Oslo neighbourhoods and reveals how rents evolve across the city.

No titles, URLs, or identifying information are collected.

## Setup

```
pip install -r requirements.txt
```

Requires Python 3.9+.

## Run

Fetch all pages until no more listings are found:

```
python fetch_listings.py
```

Output is written to `local_output/finn_listings_YYYYMMDD_HHMMSS.json` (the folder is created automatically).

## Output format

```json
{
  "fetched_at": "2026-05-01T16:45:00",
  "version": "1.1.0",
  "source": "https://www.finn.no/realestate/lettings/search.html?location=0.20061",
  "listing_count": 247,
  "listings": [
    {
      "page": 1,
      "address": "Storgata 1, Oslo",
      "postal_code": "0155",
      "price": 18500,
      "area_m2": 52,
      "property_type": "Leilighet",
      "bedrooms": 2,
      "is_agency": false
    }
  ]
}
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--max-pages N` | no limit | Stop after N pages |
| `--max-ads N` | no limit | Stop after N listings |
| `--min-delay S` | 1.0 | Minimum seconds between requests |
| `--max-delay S` | 2.0 | Maximum seconds between requests |
| `--output FILE` | auto-timestamped | Output file path |
| `--no-geocode` | off | Skip Kartverket postal code lookup |

Example — fetch at most 200 listings:

```
python fetch_listings.py --max-ads 200
```

## Geocoding

Each listing's address is extracted from the search card and stored in the `address` field. When a postal code is not directly visible in the card text, the scraper calls the [Kartverket address API](https://ws.geonorge.no/adresser/v1/) to resolve it.

Results are cached in `local_output/address_postal_lookup.json` and reused across runs to avoid redundant API calls. Pass `--no-geocode` to skip this step entirely.

## Legal considerations

Automated collection of data from finn.no is prohibited by their Terms of Service without written permission. The `robots.txt` states this explicitly.

This project is intended for personal, non-commercial research only. It is designed to minimise impact:
- Only the real estate search pages are accessed — these are explicitly allowed in finn.no's `robots.txt` (the same paths permitted for search engine indexing)
- Requests use an honest User-Agent identifying the project
- A 1–2 second delay is enforced between requests
- Only market data is collected — no personal information

Running this tool is your own responsibility. Do not use it commercially or redistribute the collected data.
