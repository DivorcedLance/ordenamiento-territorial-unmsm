import os
import urllib.request
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask

TILES = [
    'Copernicus_DSM_COG_10_S14_00_W073_00_DEM',
    'Copernicus_DSM_COG_10_S14_00_W074_00_DEM',
    'Copernicus_DSM_COG_10_S15_00_W073_00_DEM',
    'Copernicus_DSM_COG_10_S15_00_W074_00_DEM'
]
BASE_URL = 'https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com'
WORK_DIR = r'C:\Users\divor\Downloads\OT'
DEM_DIR = os.path.join(WORK_DIR, 'copernicus_dem_tiles')
os.makedirs(DEM_DIR, exist_ok=True)

downloaded_files = []
for tile in TILES:
    url = f'{BASE_URL}/{tile}/{tile}.tif'
    out_file = os.path.join(DEM_DIR, f'{tile}.tif')
    if not os.path.exists(out_file) or os.path.getsize(out_file) < 1000000:
        print(f"Descargando {tile} ({url})...")
        urllib.request.urlretrieve(url, out_file)
        print(f"Descargado: {out_file} ({os.path.getsize(out_file)/(1024*1024):.2f} MB)")
    else:
        print(f"Ya existe: {out_file}")
    downloaded_files.append(out_file)

# 1. Hacer merge de las 4 teselas
print("Haciendo mosaico (merge) de las 4 teselas de Copernicus DEM 30m...")
src_files_to_mosaic = [rasterio.open(f) for f in downloaded_files]
mosaic, out_trans = merge(src_files_to_mosaic)

out_meta = src_files_to_mosaic[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_trans,
    "crs": src_files_to_mosaic[0].crs
})

mosaic_path = os.path.join(WORK_DIR, "DEM_Copernicus_30m_Mosaico.tif")
with rasterio.open(mosaic_path, "w", **out_meta) as dest:
    dest.write(mosaic)
for s in src_files_to_mosaic:
    s.close()
print(f"Mosaico guardado: {mosaic_path}")

# 2. Recortar (clip) con el límite oficial de Aymaraes
print("Recortando con el polígono oficial de la Provincia de Aymaraes...")
gdf = gpd.read_file(os.path.join(WORK_DIR, 'aymaraes_fc.geojson'))
with rasterio.open(mosaic_path) as src:
    # Asegurar que el GeoDataFrame tenga el mismo CRS
    gdf_reproj = gdf.to_crs(src.crs)
    clipped_img, clipped_transform = mask(src, gdf_reproj.geometry, crop=True)
    clipped_meta = src.meta.copy()
    clipped_meta.update({
        "driver": "GTiff",
        "height": clipped_img.shape[1],
        "width": clipped_img.shape[2],
        "transform": clipped_transform
    })
    
clipped_path = os.path.join(WORK_DIR, "DEM_Aymaraes_Copernicus_30m.tif")
with rasterio.open(clipped_path, "w", **clipped_meta) as dest:
    dest.write(clipped_img)
print(f"¡DEM oficial de Aymaraes generado exitosamente!: {clipped_path}")
print(f"Dimensiones: {clipped_img.shape}, Altitud Min={clipped_img[clipped_img > -100].min():.1f}m, Max={clipped_img.max():.1f}m")
