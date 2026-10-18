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
                if any(k in n.lower() for k in ['pisco', 'g_05_02', 'g_05_03', 'g_05_04', 'g_06_09']):
                    matches.append((n, t))
        for n, t in matches:
            print(f"[{n}] -> {t}")
except Exception as e:
    print('Error:', e)
