import urllib.request
import xml.etree.ElementTree as ET
import re

url = 'https://idesep.senamhi.gob.pe/geoserver/wms?service=WMS&version=1.3.0&request=GetCapabilities'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        xml_data = resp.read()
        print('Capabilities size:', len(xml_data))
        root = ET.fromstring(xml_data)
        # Find all Layer names and titles
        layers = []
        for elem in root.iter('{http://www.opengis.net/wms}Layer'):
            name_el = elem.find('{http://www.opengis.net/wms}Name')
            title_el = elem.find('{http://www.opengis.net/wms}Title')
            if name_el is not None and name_el.text:
                n = name_el.text
                t = title_el.text if title_el is not None else ''
                if any(k in n.lower() or k in t.lower() for k in ['pisco', 'precip', 'temperat', 'tmax', 'tmin', 'tmed', 'bio', 'holdridge', '2026', 'ago']):
                    layers.append((n, t))
        print(f'Capas relevantes encontradas: {len(layers)}')
        for n, t in layers[:25]:
            print(f'  - {n} | {t}')
except Exception as e:
    print('Error:', e)
