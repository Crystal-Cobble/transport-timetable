"""Simulate the full disruption detection flow for Papakura Train Station."""
import urllib.request, json
from datetime import datetime

GTFS_KEY = '0b6d714ed53748ceb08b086129ed4375'
RT_KEY = '52aacd1bd356439b8a54949165d70812'
API = 'https://api.at.govt.nz'

stop = {'stopCode': '97', 'stopId': '97-cf37d972', 'stopName': 'Papakura Train Station'}

# Step 1: fetchStopDetails
print("=== Step 1: fetchStopDetails ===")
url = API + '/gtfs/v3/stops/97-cf37d972'
req = urllib.request.Request(url, headers={'Ocp-Apim-Subscription-Key': GTFS_KEY, 'Accept': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())
attrs = data.get('data', {}).get('attributes', {})
lt = attrs.get('location_type')
print(f"  locationType = {lt}")
print(f"  stop_name = {attrs.get('stop_name')}")

# Step 2: stoptrips
print("\n=== Step 2: fetchDeparturesForStop (stoptrips) ===")
today = datetime.now().strftime('%Y-%m-%d')
hour = datetime.now().hour
url2 = f"{API}/gtfs/v3/stops/97-cf37d972/stoptrips?filter[date]={today}&filter[start_hour]={hour}&filter[hour_range]=4"
req2 = urllib.request.Request(url2, headers={'Ocp-Apim-Subscription-Key': GTFS_KEY, 'Accept': 'application/json'})
data2 = json.loads(urllib.request.urlopen(req2).read())
tc = len(data2.get('data', []))
print(f"  Trip count = {tc}  (rows = {tc})")
print(f"  data.status = 'ready', data.rows.length = {tc}")

# Step 3: isTrainStation
print("\n=== Step 3: isTrainStation ===")
name = stop['stopName'].lower()
result = 'train station' in name
print(f"  stopName = '{stop['stopName']}'")
print(f"  'train station' in name = {result}")

# Step 4: Realtime feed
print("\n=== Step 4: fetchRealtimeVehicleLookup ===")
url3 = API + '/realtime/legacy'
req3 = urllib.request.Request(url3, headers={'Ocp-Apim-Subscription-Key': RT_KEY, 'Accept': 'application/json'})
rt = json.loads(urllib.request.urlopen(req3).read())
entities = rt.get('response', {}).get('entity', [])
by_trip_count = 0
for e in entities:
    tid = ''
    if e.get('trip_update'):
        tid = e['trip_update'].get('trip', {}).get('trip_id', '')
    if not tid and e.get('vehicle'):
        tid = e['vehicle'].get('trip', {}).get('trip_id', '')
    if tid:
        by_trip_count += 1
alerts = [e for e in entities if 'alert' in e]
print(f"  byTrip size ~ {by_trip_count}")
print(f"  alerts count = {len(alerts)}")
print(f"  realtimeVehicleCache.byTrip.size === 0 ? {by_trip_count == 0}")

# Step 5: getRailRoutesWithAlerts
print("\n=== Step 5: getRailRoutesWithAlerts ===")
rail_ids = ['STH-201', 'EAST-201', 'WEST-201', 'ONE-201', 'HUIA-404']
rail_alerted = set()
for e in alerts:
    ie = e.get('alert', {}).get('informed_entity', [])
    if not isinstance(ie, list):
        ie = [ie]
    for ent in ie:
        rid = ent.get('route_id', '')
        if rid in rail_ids:
            rail_alerted.add(rid)
print(f"  Rail routes with alerts: {sorted(rail_alerted)}")

# Step 6: analyzeLineStatus / isRailRouteRunning
print("\n=== Step 6: analyzeLineStatus + isRailRouteRunning ===")
route_counts = {}
for e in entities:
    rid = ''
    sr = None
    if e.get('trip_update'):
        rid = e['trip_update'].get('trip', {}).get('route_id', '')
        sr = e['trip_update'].get('trip', {}).get('schedule_relationship')
    if not rid and e.get('vehicle'):
        rid = e['vehicle'].get('trip', {}).get('route_id', '')
        sr = e['vehicle'].get('trip', {}).get('schedule_relationship')
    if rid:
        if rid not in route_counts:
            route_counts[rid] = {'active': 0, 'cancelled': 0}
        if sr == 3:
            route_counts[rid]['cancelled'] += 1
        else:
            route_counts[rid]['active'] += 1

for rid in rail_ids:
    c = route_counts.get(rid)
    if not c:
        print(f"  {rid}: NOT in counts map -> isRailRouteRunning = false")
    else:
        running = c['active'] > 0
        print(f"  {rid}: active={c['active']}, cancelled={c['cancelled']} -> isRailRouteRunning = {running}")

# Final result
print("\n=== FINAL RESULT ===")
not_running = [r for r in rail_alerted if not route_counts.get(r, {}).get('active', 0)]
print(f"  detectZeroTripStationDisruptions would return {len(not_running)} disruptions:")
for r in sorted(not_running):
    print(f"    - {r}")
if not not_running:
    print("  WARNING: No disruptions detected!")
    if not rail_alerted:
        print("  REASON: No rail routes found in service alerts")
    else:
        running_ones = [r for r in rail_alerted if route_counts.get(r, {}).get('active', 0)]
        print(f"  REASON: These alerted routes ARE running: {running_ones}")
