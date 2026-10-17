import urllib.request
import os

tiles = [
    'Copernicus_DSM_COG_10_S14_00_W073_00_DEM',
    'Copernicus_DSM_COG_10_S14_00_W074_00_DEM',
    'Copernicus_DSM_COG_10_S15_00_W073_00_DEM',
    'Copernicus_DSM_COG_10_S15_00_W074_00_DEM'
]
base = 'https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com'
for tile in tiles:
    url = f'{base}/{tile}/{tile}.tif'
    req = urllib.request.Request(url, method='HEAD')
    try:
        with urllib.request.urlopen(req) as resp:
            sz = int(resp.headers.get('Content-Length', 0)) / (1024 * 1024)
            print(f'{tile}: OK! Size={sz:.2f} MB')
    except Exception as e:
        print(f'{tile}: {e}')
