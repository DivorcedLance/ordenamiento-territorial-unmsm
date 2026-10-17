import urllib.request
import json

url = "https://earth-search.aws.element84.com/v1/search"
payload = {
    "collections": ["sentinel-2-c1-l2a"],
    "intersects": {"type": "Point", "coordinates": [-73.25, -14.34]},
    "datetime": "2024-09-01T00:00:00Z/2024-09-10T23:59:59Z",
    "limit": 2
}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Python'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    feat = data['features'][0]
    print('Item ID:', feat['id'])
    for k, v in feat['assets'].items():
        print(f"  {k}: {v.get('href')}")
