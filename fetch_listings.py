import argparse
import json
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

__version__ = "1.0.0"

LISTING_URL = "https://www.finn.no/realestate/lettings/search.html?location=0.20061"
HEADERS = {"User-Agent": f"oslo-housing-index/{__version__} (personal market research project; non-commercial)"}
<<<<<<< HEAD
=======
KARTVERKET_API = "https://ws.geonorge.no/adresser/v1/sok"
>>>>>>> d9330e9 (Initial commit with my changes)

RE_PRICE = re.compile(r'(\d{1,3}(?:[\s \xa0]\d{3})*)\s*kr')
RE_AREA = re.compile(r'(\d{1,4})\s*(?:m²|m2)')
RE_SOV = re.compile(r'(\d+)\s*soverom', re.I)
RE_FINN_HREF = re.compile(r'/realestate/lettings(?:external)?/ad\.html\?finnkode=(\d+)')
<<<<<<< HEAD
RE_POSTAL = re.compile(r'\b(\d{4})\b')
RE_AGENCY = re.compile(r'\b(?:eiendomsmegler|megler|bolig(?:salg|utleie)|AS|property|realty)\b', re.I)
RE_ADDR_CLASSES = [re.compile(c, re.I) for c in ('sf-realestate-location', 'location', 'address')]

=======
# Norwegian postal codes are 4 digits, typically preceded by ", " and followed by a capital letter (city name).
# This pattern avoids matching years, areas, or prices.
RE_POSTAL = re.compile(r'(?:,\s*|\s)(\d{4})\s+[A-ZÆØÅ]')
RE_AGENCY = re.compile(r'\b(?:eiendomsmegler|megler|bolig(?:salg|utleie)|AS|property|realty)\b', re.I)
RE_ADDR_CLASSES = [re.compile(c, re.I) for c in ('sf-realestate-location', 'location', 'address')]

_geocode_cache: dict[str, str | None] = {}


_RE_HOUSE_LETTER = re.compile(r'(\d+)\s*[A-Za-z]$')


def _kartverket_lookup(street: str, kommunenavn: str, fuzzy: bool = False) -> str | None:
    params: dict[str, str] = {'sok': street, 'kommunenavn': kommunenavn, 'treffPerSide': '1'}
    if fuzzy:
        params['fuzzy'] = 'true'
    r = requests.get(KARTVERKET_API, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    hits = r.json().get('adresser', [])
    return str(hits[0]['postnummer']) if hits else None


def geocode_postal_code(address: str) -> str | None:
    """Resolve a 'Street, Municipality' address to its Norwegian postal code via Kartverket."""
    if address in _geocode_cache:
        return _geocode_cache[address]
    parts = address.rsplit(',', 1)
    if len(parts) != 2:
        _geocode_cache[address] = None
        return None
    street, kommunenavn = parts[0].strip(), parts[1].strip()
    stripped = _RE_HOUSE_LETTER.sub(r'\1', street)
    try:
        result = (
            _kartverket_lookup(street, kommunenavn)
            # Kartverket doesn't match "12B"-style suffixes; retry with the number only.
            or (stripped != street and _kartverket_lookup(stripped, kommunenavn))
            # Last resort: fuzzy match handles accent differences (e.g. "alle" vs "allé").
            or _kartverket_lookup(street, kommunenavn, fuzzy=True)
            or None
        )
    except Exception:
        result = None
    _geocode_cache[address] = result
    return result


>>>>>>> d9330e9 (Initial commit with my changes)
PROPERTY_TYPES: list[tuple[str, str]] = [
    ('Hybel', 'Hybel'),
    ('Rom i bofellesskap', 'Rom i bofellesskap'),
    ('Garasje', 'Garasje/Parkering'),
    ('Enebolig', 'Enebolig'),
    ('Rekkehus', 'Rekkehus'),
    ('Leilighet', 'Leilighet'),
]

_url_parts = urlparse(LISTING_URL)
_base_params = [(k, v) for k, vs in parse_qs(_url_parts.query).items() for v in vs if k != 'page']

<<<<<<< HEAD

=======
>>>>>>> d9330e9 (Initial commit with my changes)
def extract_listings_from_page(soup: BeautifulSoup, page_num: int) -> list[tuple[str, dict[str, Any]]]:
    """Returns (finnkode, data) pairs; finnkode is for deduplication only."""
    results: list[tuple[str, dict[str, Any]]] = []

    for link in soup.find_all('a', href=RE_FINN_HREF):
        href = str(link.get('href', ''))
        finnkode = RE_FINN_HREF.search(href).group(1)  # type: ignore[union-attr]

        card: Any = link
        for _ in range(5):
            parent = card.parent
            if parent is None:
                break
            card = parent
            if card.name in ('article', 'li', 'section'):
                break

        card_text = card.get_text(' ', strip=True)

        data: dict[str, Any] = {
            "page": page_num,
<<<<<<< HEAD
=======
            "address": None,
>>>>>>> d9330e9 (Initial commit with my changes)
            "postal_code": None,
            "price": None,
            "area_m2": None,
            "property_type": None,
            "bedrooms": None,
            "is_agency": False,
        }

<<<<<<< HEAD
        search_text = card_text
        for pattern in RE_ADDR_CLASSES:
            addr_el = card.find(class_=pattern)
            if addr_el:
                search_text = addr_el.get_text(strip=True)
                break
        m = RE_POSTAL.search(search_text)
        if m:
            data['postal_code'] = m.group(1)
=======
        addr_el = None
        for pattern in RE_ADDR_CLASSES:
            addr_el = card.find(class_=pattern)
            if addr_el:
                break

        address_text = addr_el.get_text(strip=True) if addr_el else None
        data['address'] = address_text

        # Finn.no search cards show "Street, City" with no postal code; the regex
        # handles the case where the format ever changes to include one.
        if address_text:
            m = RE_POSTAL.search(address_text)
            if m:
                data['postal_code'] = m.group(1)
>>>>>>> d9330e9 (Initial commit with my changes)

        m = RE_PRICE.search(card_text)
        if m:
            data['price'] = int(re.sub(r'[\s\xa0]', '', m.group(1)))

        m = RE_AREA.search(card_text)
        if m:
            data['area_m2'] = int(m.group(1))

        m = RE_SOV.search(card_text)
        if m:
            data['bedrooms'] = int(m.group(1))

        for pt, label in PROPERTY_TYPES:
            if pt in card_text:
                data['property_type'] = label
                break

        data['is_agency'] = bool(RE_AGENCY.search(card_text))

        results.append((finnkode, data))

    return results


def _build_page_url(page: int) -> str:
    return urlunparse(_url_parts._replace(query=urlencode(_base_params + [('page', str(page))])))


def main(
    max_pages: int | None = None,
    max_ads: int | None = None,
    min_delay: float = 1.0,
    max_delay: float = 2.0,
    output_file: str | None = None,
<<<<<<< HEAD
=======
    geocode: bool = True,
>>>>>>> d9330e9 (Initial commit with my changes)
) -> list[dict[str, Any]]:
    """Crawl listing pages and extract aggregate market data (no individual ad visits)."""
    page = 1
    seen_finnkodes: set[str] = set()
    all_data: list[dict[str, Any]] = []
    dupe_pages: list[tuple[int, int]] = []

    while True:
        if max_pages is not None and page > max_pages:
            print(f'Reached max_pages limit: {max_pages}')
            break

        print(f'Page {page} ...', end=' ', flush=True)
        try:
            r = requests.get(_build_page_url(page), headers=HEADERS, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print(f'error: {e}')
            break

        soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
        page_listings = extract_listings_from_page(soup, page)

        if not page_listings:
            print('no listings found - stopping')
            break

        new = [(fk, d) for fk, d in page_listings if fk not in seen_finnkodes]
        skipped = len(page_listings) - len(new)
        if skipped:
            dupe_pages.append((page, skipped))
        print(f'{len(new)} listings')

        if not new:
            print(f'No new listings on page {page} - stopping')
            break

        if max_ads is not None:
            new = new[:max_ads - len(all_data)]
        for finnkode, data in new:
            seen_finnkodes.add(finnkode)
<<<<<<< HEAD
=======
            if geocode and data['postal_code'] is None and data.get('address'):
                data['postal_code'] = geocode_postal_code(data['address'])
                time.sleep(0.1)
>>>>>>> d9330e9 (Initial commit with my changes)
            all_data.append(data)
        if max_ads is not None and len(all_data) >= max_ads:
            print(f'Reached max_ads limit: {max_ads}')
            break

        page += 1
        time.sleep(random.uniform(min_delay, max_delay))

    now = datetime.now()
    timestamp_slug = now.strftime('%Y%m%d_%H%M%S')
    out = Path(output_file or f'local_output/finn_listings_{timestamp_slug}.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "fetched_at": now.isoformat(timespec='seconds'),
        "version": __version__,
        "source": LISTING_URL,
        "listing_count": len(all_data),
        "listings": all_data,
    }
    with out.open('w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    total_dupes = sum(n for _, n in dupe_pages)
    dupe_summary = ', '.join(f'p{p}:{n}' for p, n in dupe_pages) if dupe_pages else 'none'
    print(f'\nWrote {out} with {len(all_data)} entries')
    print(f'Cross-page duplicates: {total_dupes} (pages: {dupe_summary})')
    return all_data


def _cli() -> None:
    p = argparse.ArgumentParser(description='Fetch rental listings from FINN with pagination')
    p.add_argument('--max-pages', type=int, default=None)
    p.add_argument('--max-ads', type=int, default=None)
    p.add_argument('--min-delay', type=float, default=1.0)
    p.add_argument('--max-delay', type=float, default=2.0)
    p.add_argument('--output', type=str, default=None)
<<<<<<< HEAD
=======
    p.add_argument('--no-geocode', action='store_true', help='Skip Kartverket postal code lookup')
>>>>>>> d9330e9 (Initial commit with my changes)
    args = p.parse_args()
    main(
        max_pages=args.max_pages,
        max_ads=args.max_ads,
        min_delay=args.min_delay,
        max_delay=args.max_delay,
        output_file=args.output,
<<<<<<< HEAD
=======
        geocode=not args.no_geocode,
>>>>>>> d9330e9 (Initial commit with my changes)
    )


if __name__ == '__main__':
    _cli()
