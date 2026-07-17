#!/usr/bin/env python3
"""Refresh the local fallback of AT bus, train and ferry stops."""
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "map-backups" / "transport-stops.js"
source = (ROOT / "map.html").read_text(encoding="utf-8")
match = re.search(r"const AT_API_KEY='([^']+)'", source)
if not match:
    raise RuntimeError("AT_API_KEY was not found in map.html")
request = urllib.request.Request("https://api.at.govt.nz/gtfs/v3/stops", headers={"Ocp-Apim-Subscription-Key": match.group(1), "Accept": "application/vnd.api+json", "User-Agent": "transport-timetable-backup/1.0"})
with urllib.request.urlopen(request, timeout=90) as response:
    body = json.load(response)
stops = [item.get("attributes", item) for item in body.get("data", [])]
if not stops:
    raise RuntimeError("AT returned no stop locations")
payload = {"updated": datetime.now(timezone.utc).isoformat(), "stops": stops}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("window.AT_TRANSPORT_STOPS=" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"Saved {len(stops):,} AT stop locations to {OUTPUT.relative_to(ROOT)}")
