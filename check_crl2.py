import csv, os

temp = os.environ['TEMP']

# Check if ANY trips stop at CRL tunnel stations
crl_stop_ids = set()
with open(os.path.join(temp, 'at_gtfs', 'stops.txt')) as f:
    for row in csv.DictReader(f):
        name = row['stop_name']
        if 'Karanga-a-Hape' in name or 'Te Waihorotiu' in name:
            crl_stop_ids.add(row['stop_id'])
            print(f"CRL stop: {row['stop_id']} = {name}")

print(f"\nSearching stop_times for {len(crl_stop_ids)} CRL stop IDs...")

# Search stop_times
crl_trips = set()
count = 0
with open(os.path.join(temp, 'at_gtfs', 'stop_times.txt')) as f:
    for row in csv.DictReader(f):
        if row['stop_id'] in crl_stop_ids:
            crl_trips.add(row['trip_id'])
            count += 1

print(f"Found {count} stop_time entries at CRL stations, across {len(crl_trips)} trips")

if crl_trips:
    # Check what routes these trips belong to
    trips = {}
    with open(os.path.join(temp, 'at_gtfs', 'trips.txt')) as f:
        for row in csv.DictReader(f):
            if row['trip_id'] in crl_trips:
                trips[row['trip_id']] = row

    route_counts = {}
    for t in trips.values():
        key = f"{t['route_id']} | {t['trip_headsign']}"
        route_counts[key] = route_counts.get(key, 0) + 1

    print("\nRoutes using CRL stations:")
    for k, v in sorted(route_counts.items()):
        print(f"  [{v:3d}] {k}")

    # Show stop sequence for one CRL trip
    sample_trip = list(crl_trips)[0]
    print(f"\nSample CRL trip: {sample_trip}")
    print(f"Route: {trips[sample_trip]['route_id']} | {trips[sample_trip]['trip_headsign']}")
    print(f"Shape: {trips[sample_trip]['shape_id']}")

    stops = {}
    with open(os.path.join(temp, 'at_gtfs', 'stops.txt')) as f:
        for row in csv.DictReader(f):
            stops[row['stop_id']] = row

    sample_stops = []
    with open(os.path.join(temp, 'at_gtfs', 'stop_times.txt')) as f:
        for row in csv.DictReader(f):
            if row['trip_id'] == sample_trip:
                sample_stops.append(row)

    sample_stops.sort(key=lambda x: int(x['stop_sequence']))
    for st in sample_stops:
        s = stops.get(st['stop_id'], {})
        crl_marker = " <-- CRL" if st['stop_id'] in crl_stop_ids else ""
        print(f"  {int(st['stop_sequence']):3d}  {s.get('stop_name','?'):35s}  ({s.get('stop_lat','')}, {s.get('stop_lon','')}){crl_marker}")
