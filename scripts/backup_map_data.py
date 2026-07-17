#!/usr/bin/env python3
"""Create local JSON snapshots of the non-transport map layers."""

from __future__ import annotations

import json
import argparse
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "map-backups"
# Auckland Council coverage used by the live map, in south/west/north/east order.
AUCKLAND_BBOX = "-37.2926,174.3289,-36.3911,175.6288"
OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
SELECTORS = {
    "bike": [
        'nwr[amenity~"bicycle_parking|bicycle_repair_station|bicycle_rental"]',
        "nwr[service=bicycle_repair]",
    ],
    "commercial": [
        "nwr[landuse=commercial][name]",
        "nwr[shop][name]",
        'nwr[amenity~"cafe|restaurant|fast_food|bar|marketplace|food_court"][name]',
        'nwr[tourism~"hotel|hostel|motel|guest_house"][name]',
    ],
    "culture": [
        'nwr[tourism~"museum|gallery|attraction"][name]',
        'nwr[amenity~"library|school|university|college|kindergarten|theatre|cinema|community_centre|arts_centre"][name]',
    ],
    "recreation": [
        'nwr[leisure~"park|playground|recreation_ground|sports_centre|stadium|fitness_centre|swimming_pool|pitch|garden"][name]',
        'nwr[tourism~"beach|viewpoint|zoo"][name]',
        "nwr[natural=beach][name]",
    ],
    "facilities": [
        'nwr[amenity~"toilets|drinking_water"]',
        'nwr[amenity~"hospital|clinic|doctors|pharmacy"]',
        'nwr[amenity~"police|fire_station"]',
        'nwr[amenity~"fuel|bank|atm|post_office"]',
        "nwr[tourism=information]",
    ],
}


def request_json(url: str, data: bytes | None = None) -> dict | list:
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": "transport-timetable-backup/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def fetch_category(category: str, bbox: str) -> list[dict]:
    combined: dict[str, dict] = {}
    for selector in SELECTORS[category]:
        query = f"[out:json][timeout:80];{selector}({bbox});out center tags;"
        body = urllib.parse.urlencode({"data": query}).encode()
        last_error: Exception | None = None
        for attempt in range(6):
            endpoint = OVERPASS_ENDPOINTS[attempt % len(OVERPASS_ENDPOINTS)]
            try:
                result = request_json(endpoint, body)
                elements = result.get("elements") if isinstance(result, dict) else None
                if not isinstance(elements, list):
                    raise RuntimeError("Overpass returned invalid data")
                for element in elements:
                    combined[f"{element.get('type')}/{element.get('id')}"] = element
                break
            except Exception as error:  # retry the alternate endpoint
                last_error = error
                time.sleep(min(2**attempt, 20))
        else:
            raise RuntimeError(f"Unable to back up {category}: {selector}") from last_error
    return list(combined.values())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="keep snapshots that already exist")
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    bbox = AUCKLAND_BBOX
    manifest = {"generated_at": generated_at, "bbox": bbox, "categories": {}}
    snapshots = {}
    for category in SELECTORS:
        path = OUTPUT_DIR / f"{category}.json"
        if path.exists() and args.resume:
            payload = json.loads(path.read_text(encoding="utf-8"))
            count = len(payload.get("elements", []))
            snapshots[category] = payload
            manifest["categories"][category] = {"file": path.name, "count": count}
            print(f"Keeping {category}: {count:,} saved elements", flush=True)
            continue
        print(f"Backing up {category}...", flush=True)
        elements = fetch_category(category, bbox)
        payload = {
            "category": category,
            "generated_at": generated_at,
            "bbox": bbox,
            "source": "OpenStreetMap via Overpass API",
            "elements": elements,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        snapshots[category] = payload
        manifest["categories"][category] = {"file": path.name, "count": len(elements)}
        print(f"  saved {len(elements):,} elements", flush=True)
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    bundle = "window.MAP_BACKUPS=" + json.dumps(
        snapshots, ensure_ascii=False, separators=(",", ":")
    ) + ";\n"
    (OUTPUT_DIR / "map-backups.js").write_text(bundle, encoding="utf-8")


if __name__ == "__main__":
    main()
