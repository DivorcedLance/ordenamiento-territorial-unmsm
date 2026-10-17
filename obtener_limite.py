import urllib.request
import urllib.parse
import json

overpass_url = "https://overpass-api.de/api/interpreter"
query = """[out:json][timeout:25];
relation["name"="Provincia de Aymaraes"]["admin_level"="6"];
out geom;
"""

req = urllib.request.Request(overpass_url, data=query.encode('utf-8'))
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Elements found: {len(data.get('elements', []))}")
        if data.get('elements'):
            print("Encontrado en OSM!")
except Exception as e:
    print("Error:", e)
