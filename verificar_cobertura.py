import urllib.request
import json

url = "https://earth-search.aws.element84.com/v1/search"
payload = {
    "collections": ["sentinel-2-c1-l2a"],
    "bbox": [-73.58, -14.85, -72.98, -13.80],
    "datetime": "2024-09-08T00:00:00Z/2024-09-08T23:59:59Z",
    "limit": 10
}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Python'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"Tiles on 2024-09-08 covering Aymaraes: {len(data['features'])}")
    for f in data['features']:
        print(f"  - {f['id']} | Cloud: {f['properties']['eo:cloud_cover']}% | bbox: {f['bbox']}")
