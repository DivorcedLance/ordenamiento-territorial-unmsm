import urllib.request
import xml.etree.ElementTree as ET

url = 'https://idesep.senamhi.gob.pe/geoserver/wms?service=WMS&version=1.3.0&request=GetCapabilities'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_data = resp.read()
        root = ET.fromstring(xml_data)
        matches = []
        for elem in root.iter('{http://www.opengis.net/wms}Layer'):
            name_el = elem.find('{http://www.opengis.net/wms}Name')
            title_el = elem.find('{http://www.opengis.net/wms}Title')
            if name_el is not None and name_el.text:
                n = name_el.text
                t = title_el.text if title_el is not None else ''
                # Look specifically for Agosto, Climatologia, PISCO, Precipitación mensual, etc.
                if 'agosto' in t.lower() or 'pisco' in t.lower() or 'precipitación mensual' in t.lower() or 'temperatura media' in t.lower():
                    matches.append((n, t))
        print(f"Total coincidencias: {len(matches)}")
        for n, t in matches[:40]:
            print(f"  [{n}] -> {t}")
except Exception as e:
    print('Error:', e)
