import csv, os

temp = os.environ['TEMP']

# Load stops
stops = {}
with open(os.path.join(temp, 'at_gtfs', 'stops.txt')) as f:
    for row in csv.DictReader(f):
        stops[row['stop_id']] = row

# Check stop sequence for a Western line full trip (Brit 2 To Swanson)
trips = list(csv.DictReader(open(os.path.join(temp, 'at_gtfs', 'trips.txt'))))
west_full = [t for t in trips if t['route_id'] == 'WEST-201' and 'Swanson 1 Via Newmarket' in t['trip_headsign']]
trip_id = west_full[0]['trip_id']
print(f"Checking stops for trip: {trip_id}")
print(f"Headsign: {west_full[0]['trip_headsign']}\n")

# Load stop_times for this trip
stop_times = []
with open(os.path.join(temp, 'at_gtfs', 'stop_times.txt')) as f:
    for row in csv.DictReader(f):
        if row['trip_id'] == trip_id:
            stop_times.append(row)

stop_times.sort(key=lambda x: int(x['stop_sequence']))
for st in stop_times:
    stop = stops.get(st['stop_id'], {})
    name = stop.get('stop_name', '?')
    lat = stop.get('stop_lat', '?')
    lon = stop.get('stop_lon', '?')
    print(f"  {int(st['stop_sequence']):3d}  {st['stop_id']:20s}  {name:35s}  ({lat}, {lon})")

print("\n--- Now checking Southern line (Brit 4 To Pukekohe) ---")
south_full = [t for t in trips if t['route_id'] == 'STH-201' and 'Brit 4 To Pukekohe 3 Via NKT 4, OHU 3, Papakura 1' in t['trip_headsign']]
trip_id2 = south_full[0]['trip_id']
print(f"Checking stops for trip: {trip_id2}")

stop_times2 = []
with open(os.path.join(temp, 'at_gtfs', 'stop_times.txt')) as f:
    for row in csv.DictReader(f):
        if row['trip_id'] == trip_id2:
            stop_times2.append(row)

stop_times2.sort(key=lambda x: int(x['stop_sequence']))
for st in stop_times2:
    stop = stops.get(st['stop_id'], {})
    name = stop.get('stop_name', '?')
    print(f"  {int(st['stop_sequence']):3d}  {st['stop_id']:20s}  {name}")
