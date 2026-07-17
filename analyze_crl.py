import csv, os

temp = os.environ['TEMP']

# Load stops to find CRL station coordinates
stops = {}
with open(os.path.join(temp, 'at_gtfs', 'stops.txt')) as f:
    for row in csv.DictReader(f):
        stops[row['stop_id']] = row

# CRL station IDs we found
crl_names = ['Karanga-a-Hape', 'Te Waihorotiu', 'Waitemata', 'Grafton']
for sid, s in stops.items():
    if any(c in s['stop_name'] for c in crl_names):
        print(f"{s['stop_id']:20s} {s['stop_name']:30s} lat={s['stop_lat']} lon={s['stop_lon']} type={s.get('location_type','')}")

print("\n--- Checking Western line trip variants ---")
trips = list(csv.DictReader(open(os.path.join(temp, 'at_gtfs', 'trips.txt'))))
west_trips = [t for t in trips if t['route_id'] == 'WEST-201']
headsigns = set(t['trip_headsign'] for t in west_trips)
for h in sorted(headsigns):
    count = sum(1 for t in west_trips if t['trip_headsign'] == h)
    # Get one shape
    shape = next(t['shape_id'] for t in west_trips if t['trip_headsign'] == h)
    print(f"  [{count:3d}] {h:50s} shape={shape}")

print("\n--- Checking Southern line trip variants ---")
south_trips = [t for t in trips if t['route_id'] == 'STH-201']
headsigns = set(t['trip_headsign'] for t in south_trips)
for h in sorted(headsigns):
    count = sum(1 for t in south_trips if t['trip_headsign'] == h)
    shape = next(t['shape_id'] for t in south_trips if t['trip_headsign'] == h)
    print(f"  [{count:3d}] {h:50s} shape={shape}")

print("\n--- Checking Eastern line trip variants ---")
east_trips = [t for t in trips if t['route_id'] == 'EAST-201']
headsigns = set(t['trip_headsign'] for t in east_trips)
for h in sorted(headsigns):
    count = sum(1 for t in east_trips if t['trip_headsign'] == h)
    shape = next(t['shape_id'] for t in east_trips if t['trip_headsign'] == h)
    print(f"  [{count:3d}] {h:50s} shape={shape}")
