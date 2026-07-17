"""Test stoptrips for Papakura."""
import urllib.request, json

GTFS_KEY = '0b6d714ed53748ceb08b086129ed4375'

# Search for Papakura stops
url = 'https://api.at.govt.nz/gtfs/v3/stops?filter[stop_name]=*Papakura*Train*&page[limit]=10'
req = urllib.request.Request(url, headers={'Ocp-Apim-Subscription-Key': GTFS_KEY, 'Accept': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())
print("Search for Papakura Train:")
for item in data.get('data', []):
    a = item.get('attributes', {})
    sid = a.get('stop_id', '')
    code = a.get('stop_code', '')
    name = a.get('stop_name', '')
    lt = a.get('location_type', '')
    print(f"  sid={sid}, code={code}, name={name}, loc_type={lt}")
    
    # Try stoptrips
    surl = f'https://api.at.govt.nz/gtfs/v3/stops/{sid}/stoptrips'
    sreq = urllib.request.Request(surl, headers={'Ocp-Apim-Subscription-Key': GTFS_KEY, 'Accept': 'application/json'})
    try:
        sdata = json.loads(urllib.request.urlopen(sreq).read())
        print(f"    stoptrips: {len(sdata.get('data', []))} trips")
    except Exception as e:
        print(f"    stoptrips ERROR: {e}")

# Also check by stop code 97
print("\nSearch by stop_code=97:")
url2 = f'https://api.at.govt.nz/gtfs/v3/stops?filter[stop_code]=97&page[limit]=5'
req2 = urllib.request.Request(url2, headers={'Ocp-Apim-Subscription-Key': GTFS_KEY, 'Accept': 'application/json'})
data2 = json.loads(urllib.request.urlopen(req2).read())
for item in data2.get('data', []):
    a = item.get('attributes', {})
    sid = a.get('stop_id', '')
    code = a.get('stop_code', '')
    name = a.get('stop_name', '')
    lt = a.get('location_type', '')
    print(f"  sid={sid}, code={code}, name={name}, loc_type={lt}")
    
    surl = f'https://api.at.govt.nz/gtfs/v3/stops/{sid}/stoptrips'
    sreq = urllib.request.Request(surl, headers={'Ocp-Apim-Subscription-Key': GTFS_KEY, 'Accept': 'application/json'})
    try:
        sdata = json.loads(urllib.request.urlopen(sreq).read())
        print(f"    stoptrips: {len(sdata.get('data', []))} trips")
    except Exception as e:
        print(f"    stoptrips ERROR: {e}")
