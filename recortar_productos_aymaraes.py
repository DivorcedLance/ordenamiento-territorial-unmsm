import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np

WORK_DIR = r"C:\Users\divor\Downloads\OT"
BAND_DIR = os.path.join(WORK_DIR, "sentinel2_bands")
CLIPPED_DIR = os.path.join(WORK_DIR, "productos_aymaraes_procesados")
os.makedirs(CLIPPED_DIR, exist_ok=True)

gdf = gpd.read_file(os.path.join(WORK_DIR, "aymaraes_fc.geojson"))

print("Recortando bandas analíticas con el polígono oficial de Aymaraes...")
for fname in os.listdir(BAND_DIR):
    if not (fname.endswith('.tiff') or fname.endswith('.tif')):
        continue
    in_path = os.path.join(BAND_DIR, fname)
    with rasterio.open(in_path) as src:
        gdf_reproj = gdf.to_crs(src.crs)
        clipped_img, clipped_transform = mask(src, gdf_reproj.geometry, crop=True)
        clipped_meta = src.meta.copy()
        clipped_meta.update({
            "height": clipped_img.shape[1],
            "width": clipped_img.shape[2],
            "transform": clipped_transform
        })
        
        # Generar nombre limpio
        tag = "True_color"
        if "B04" in fname:
            tag = "B04_Red"
        elif "B08" in fname:
            tag = "B08_NIR"
        elif "NDVI" in fname:
            tag = "NDVI_16bit"
        elif "NDWI" in fname:
            tag = "NDWI_16bit"
            
        out_name = f"Aymaraes_Sentinel2_{tag}.tif"
        out_path = os.path.join(CLIPPED_DIR, out_name)
        with rasterio.open(out_path, "w", **clipped_meta) as dst:
            dst.write(clipped_img)
            
        print(f"  -> Guardado: {out_name} (shape: {clipped_img.shape})")

print("\n¡Todos los productos analíticos recortados a la Provincia de Aymaraes están listos!")
