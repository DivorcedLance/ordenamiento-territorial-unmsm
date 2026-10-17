import urllib.request
import json

url = "https://earth-search.aws.element84.com/v1/search"
payload = {
    "collections": ["sentinel-2-c1-l2a", "sentinel-2-l2a"],
    "intersects": {
        "type": "Point",
        "coordinates": [-73.25, -14.34]
    },
    "datetime": "2024-05-01T00:00:00Z/2024-10-17T23:59:59Z",
    "query": {
        "eo:cloud_cover": {"lt": 10}
    },
    "limit": 10,
    "sortby": [
        {"field": "properties.datetime", "direction": "desc"}
    ]
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Python'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        features = data.get('features', [])
        print(f"Total escenas con baja nubosidad encontradas sobre Aymaraes: {len(features)}")
        for f in features[:6]:
            dt = f['properties'].get('datetime')
            cc = f['properties'].get('eo:cloud_cover')
            fid = f['id']
            print(f"- ID: {fid} | Fecha: {dt} | Nubosidad: {cc:.1f}%")
except Exception as e:
    print("Error:", e)
