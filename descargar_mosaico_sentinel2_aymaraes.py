import os
import json
import urllib.request
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
import numpy as np
import matplotlib.pyplot as plt

WORK_DIR = r"C:\Users\divor\Downloads\OT"
OUT_DIR = os.path.join(WORK_DIR, "productos_aymaraes_finales")
os.makedirs(OUT_DIR, exist_ok=True)

gdf = gpd.read_file(os.path.join(WORK_DIR, "aymaraes_fc.geojson"))

# 4 teselas que cubren el 100% de Aymaraes en la fecha óptima sin nubes (2024-09-08)
TILES = [
    "S2A_T18LXK_20240908T151216_L2A",
    "S2A_T18LYK_20240908T151216_L2A",
    "S2A_T18LXJ_20240908T151216_L2A",
    "S2A_T18LYJ_20240908T151216_L2A"
]

BASE_S3 = "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/18"

# Mapeo de rutas de teselas
tile_paths = {
    "S2A_T18LXK_20240908T151216_L2A": "L/XK/2024/9/S2A_T18LXK_20240908T151216_L2A",
    "S2A_T18LYK_20240908T151216_L2A": "L/YK/2024/9/S2A_T18LYK_20240908T151216_L2A",
    "S2A_T18LXJ_20240908T151216_L2A": "L/XJ/2024/9/S2A_T18LXJ_20240908T151216_L2A",
    "S2A_T18LYJ_20240908T151216_L2A": "L/YJ/2024/9/S2A_T18LYJ_20240908T151216_L2A"
}

def get_band_url(tile_id, band):
    rel = tile_paths[tile_id]
    return f"{BASE_S3}/{rel}/{band}.tif"

print("Descargando y recortando bandas Sentinel-2 (B02, B03, B04, B08, B11, TCI) para Aymaraes...")

bands_to_process = {
    "red": "B04",
    "nir": "B08",
    "green": "B03",
    "blue": "B02",
    "swir": "B11",
    "visual": "TCI"
}

# Procesar cada banda: abrir vía GDAL/rasterio COG stream, recortar con Aymaraes, y guardar mosaico
mosaicos = {}

for band_key, band_code in bands_to_process.items():
    print(f"\n--- Procesando Banda: {band_code} ({band_key}) ---")
    clipped_tiles = []
    
    for tile_id in TILES:
        url = get_band_url(tile_id, band_code)
        vsicurl_url = f"/vsicurl/{url}"
        try:
            with rasterio.open(vsicurl_url) as src:
                # Reproyectar geometría a la proyección de la imagen (UTM 18S)
                gdf_utm = gdf.to_crs(src.crs)
                # Verificar si la geometría interseca el bounding box de la tesela
                if src.bounds.left <= gdf_utm.total_bounds[2] and src.bounds.right >= gdf_utm.total_bounds[0] and \
                   src.bounds.bottom <= gdf_utm.total_bounds[3] and src.bounds.top >= gdf_utm.total_bounds[1]:
                    out_img, out_transform = mask(src, gdf_utm.geometry, crop=True, nodata=0)
                    if out_img.max() > 0:
                        meta = src.meta.copy()
                        meta.update({
                            "height": out_img.shape[1],
                            "width": out_img.shape[2],
                            "transform": out_transform,
                            "nodata": 0
                        })
                        # Guardar temporal
                        tmp_name = os.path.join(OUT_DIR, f"tmp_{tile_id}_{band_code}.tif")
                        with rasterio.open(tmp_name, "w", **meta) as tmp_dst:
                            tmp_dst.write(out_img)
                        clipped_tiles.append(tmp_name)
                        print(f"  Tesela {tile_id}: intersección válida.")
        except Exception as e:
            print(f"  Error en tesela {tile_id}: {e}")
            
    if clipped_tiles:
        print(f"Mosaico para banda {band_code} con {len(clipped_tiles)} teselas...")
        src_files = [rasterio.open(f) for f in clipped_tiles]
        mos, mos_trans = merge(src_files, nodata=0)
        
        mos_meta = src_files[0].meta.copy()
        mos_meta.update({
            "height": mos.shape[1],
            "width": mos.shape[2],
            "transform": mos_trans,
            "count": mos.shape[0]
        })
        
        final_band_path = os.path.join(OUT_DIR, f"Aymaraes_Sentinel2_{band_code}.tif")
        with rasterio.open(final_band_path, "w", **mos_meta) as dst:
            dst.write(mos)
        mosaicos[band_key] = final_band_path
        print(f"Banda final guardada: {final_band_path} | Shape: {mos.shape}")
        
        # Limpiar temporales
        for s in src_files:
            s.close()
        for f in clipped_tiles:
            try:
                os.remove(f)
            except Exception:
                pass

print("\n--- Calculando Índices Espectrales Científicos para Aymaraes ---")

with rasterio.open(mosaicos["red"]) as src_r, rasterio.open(mosaicos["nir"]) as src_n, rasterio.open(mosaicos["green"]) as src_g, rasterio.open(mosaicos["blue"]) as src_b:
    r = src_r.read(1).astype(np.float32)
    nir = src_n.read(1).astype(np.float32)
    g = src_g.read(1).astype(np.float32)
    b = src_b.read(1).astype(np.float32)
    
    meta_idx = src_r.meta.copy()
    meta_idx.update({"dtype": "float32", "nodata": -9999.0, "count": 1})
    
    # 1. NDVI = (NIR - Red) / (NIR + Red)
    val_ndvi = (nir + r) > 0
    ndvi = np.full_like(r, -9999.0, dtype=np.float32)
    ndvi[val_ndvi] = (nir[val_ndvi] - r[val_ndvi]) / (nir[val_ndvi] + r[val_ndvi])
    ndvi_path = os.path.join(OUT_DIR, "Aymaraes_NDVI_10m.tif")
    with rasterio.open(ndvi_path, "w", **meta_idx) as dst:
        dst.write(ndvi, 1)
    print(f"NDVI 10m: Min={np.min(ndvi[val_ndvi]):.3f}, Media={np.mean(ndvi[val_ndvi]):.3f}, Max={np.max(ndvi[val_ndvi]):.3f}")
    
    # 2. NDWI = (Green - NIR) / (Green + NIR) (McFeeters)
    val_ndwi = (g + nir) > 0
    ndwi = np.full_like(r, -9999.0, dtype=np.float32)
    ndwi[val_ndwi] = (g[val_ndwi] - nir[val_ndwi]) / (g[val_ndwi] + nir[val_ndwi])
    ndwi_path = os.path.join(OUT_DIR, "Aymaraes_NDWI_10m.tif")
    with rasterio.open(ndwi_path, "w", **meta_idx) as dst:
        dst.write(ndwi, 1)
    print(f"NDWI 10m: Min={np.min(ndwi[val_ndwi]):.3f}, Media={np.mean(ndwi[val_ndwi]):.3f}, Max={np.max(ndwi[val_ndwi]):.3f}")
    
    # 3. EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 10000) (para biomasa de Holdridge)
    denom_evi = (nir + 6.0*r - 7.5*b + 10000.0)
    val_evi = val_ndvi & (denom_evi != 0)
    evi = np.full_like(r, -9999.0, dtype=np.float32)
    evi[val_evi] = 2.5 * ((nir[val_evi] - r[val_evi]) / denom_evi[val_evi])
    evi_path = os.path.join(OUT_DIR, "Aymaraes_EVI_10m.tif")
    with rasterio.open(evi_path, "w", **meta_idx) as dst:
        dst.write(evi, 1)
    print(f"EVI 10m: Min={np.min(evi[val_evi]):.3f}, Media={np.mean(evi[val_evi]):.3f}, Max={np.max(evi[val_evi]):.3f}")

# Generar mapa cuádruple de alta resolución para el examen parcial
print("\nGenerando mapa cartográfico de 4 paneles para el Examen Parcial...")
dem_path = os.path.join(WORK_DIR, "DEM_Aymaraes_Copernicus_30m.tif")

with rasterio.open(dem_path) as s_dem:
    dem_raw = s_dem.read(1)
    dem_val = np.where(dem_raw > 0, dem_raw, np.nan)

with rasterio.open(mosaicos["visual"]) as s_vis:
    vis_r = s_vis.read([1, 2, 3])
    # Normalizar para visualización RGB
    vis_rgb = np.clip(vis_r.transpose(1, 2, 0) / 255.0, 0, 1)

fig, axes = plt.subplots(2, 2, figsize=(16, 16), dpi=300)

# Panel (0,0): True Color RGB
axes[0, 0].imshow(vis_rgb)
axes[0, 0].set_title("A) Sentinel-2 L2A: Color Real (RGB 10m)\nProvincia de Aymaraes (Apurímac)", fontsize=13, fontweight="bold")
axes[0, 0].axis("off")

# Panel (0,1): Copernicus DEM GLO-30
im_dem = axes[0, 1].imshow(dem_val, cmap="terrain")
axes[0, 1].set_title("B) Copernicus DEM GLO-30 (30m)\nTopografía, Relieve y Cuencas Hidrográficas", fontsize=13, fontweight="bold")
axes[0, 1].axis("off")
cb1 = plt.colorbar(im_dem, ax=axes[0, 1], fraction=0.046, pad=0.04)
cb1.set_label("Altitud (m s.n.m.)", fontsize=10)

# Panel (1,0): NDVI 10m
ndvi_plot = np.where(ndvi != -9999.0, ndvi, np.nan)
im_ndvi = axes[1, 0].imshow(ndvi_plot, cmap="YlGn", vmin=-0.05, vmax=0.75)
axes[1, 0].set_title("C) NDVI Científico 10m (Sentinel-2 L2A)\nVigor Vegetal y Potencial Biótico (Holdridge)", fontsize=13, fontweight="bold")
axes[1, 0].axis("off")
cb2 = plt.colorbar(im_ndvi, ax=axes[1, 0], fraction=0.046, pad=0.04)
cb2.set_label("NDVI", fontsize=10)

# Panel (1,1): NDWI 10m
ndwi_plot = np.where(ndwi != -9999.0, ndwi, np.nan)
im_ndwi = axes[1, 1].imshow(ndwi_plot, cmap="BrBG", vmin=-0.5, vmax=0.3)
axes[1, 1].set_title("D) NDWI 10m (Sentinel-2 L2A)\nBalance Hídrico, Humedad del Suelo y Red Fluvial", fontsize=13, fontweight="bold")
axes[1, 1].axis("off")
cb3 = plt.colorbar(im_ndwi, ax=axes[1, 1], fraction=0.046, pad=0.04)
cb3.set_label("NDWI", fontsize=10)

plt.suptitle("COMPENDIO CARTOGRÁFICO MAESTRO: AYMARAES (APURÍMAC)\nSentinel-2 L2A (10m) + Copernicus DEM GLO-30 (30m) — Ordenamiento Territorial", fontsize=16, fontweight="bold", y=0.98)
plt.tight_layout()
final_map_png = os.path.join(WORK_DIR, "Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.png")
plt.savefig(final_map_png, bbox_inches="tight")
plt.close()

print(f"\n¡MAPA CARTOGRÁFICO MAESTRO GENERADO EXITOSAMENTE!: {final_map_png}")
