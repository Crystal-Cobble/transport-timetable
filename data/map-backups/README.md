# Map facility snapshots

The JSON files are the source snapshots for bike, commercial, culture and
learning, parks and recreation, and useful-facility markers. The refresh script
also generates `map-backups.js`, which lets `map.html` load the snapshots when
opened directly with a `file://` URL. Website visitors do not query Overpass.

Refresh every snapshot from OpenStreetMap with:

```powershell
python scripts\backup_map_data.py
```

If a refresh is interrupted, keep completed files and fetch only missing ones:

```powershell
python scripts\backup_map_data.py --resume
```

The generated `manifest.json` records the snapshot time, Auckland bounding box,
file names, and location counts. OpenStreetMap data is © OpenStreetMap
contributors and is available under the ODbL.
