import urllib.request
import xml.etree.ElementTree as ET

url = 'https://idesep.senamhi.gob.pe/geoserver/wcs?service=WCS&version=1.1.1&request=GetCapabilities'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_data = resp.read()
        root = ET.fromstring(xml_data)
        coverages = []
        for elem in root.iter('{http://www.opengis.net/wcs/1.1.1}CoverageSummary'):
            ident = elem.find('{http://www.opengis.net/wcs/1.1.1}Identifier')
            title = elem.find('{http://www.opengis.net/wcs/1.1.1}Title')
            if ident is not None and ident.text:
                i_txt = ident.text
                t_txt = title.text if title is not None else ''
                if any(k in i_txt.lower() or k in t_txt.lower() for k in ['agosto', 'pisco', 'g_05_02', 'g_05_03', 'g_05_04', 'g_06_09']):
                    coverages.append((i_txt, t_txt))
        print(f"Total coberturas WCS encontradas: {len(coverages)}")
        for i_txt, t_txt in coverages[:30]:
            print(f"  [{i_txt}] -> {t_txt}")
except Exception as e:
    print('Error:', e)
