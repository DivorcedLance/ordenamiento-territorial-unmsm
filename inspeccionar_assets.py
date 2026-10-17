import urllib.request
import json

url = "https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a/items/S2B_18LXK_20240903_0_L2A"
req = urllib.request.Request(url, headers={'User-Agent': 'Python'})
try:
    with urllib.request.urlopen(req) as resp:
        item = json.loads(resp.read().decode('utf-8'))
        print("Assets disponibles:")
        for k in ['red', 'nir', 'green', 'blue', 'visual', 'scl']:
            if k in item['assets']:
                print(f"  {k}: {item['assets'][k]['href']}")
except Exception as e:
    print("Error:", e)
