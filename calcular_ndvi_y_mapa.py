import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt

WORK_DIR = r"C:\Users\divor\Downloads\OT"
CLIPPED_DIR = os.path.join(WORK_DIR, "productos_aymaraes_procesados")

b04_path = os.path.join(CLIPPED_DIR, "Aymaraes_Sentinel2_B04_Red.tif")
b08_path = os.path.join(CLIPPED_DIR, "Aymaraes_Sentinel2_B08_NIR.tif")
dem_path = os.path.join(WORK_DIR, "DEM_Aymaraes_Copernicus_30m.tif")
rgb_path = os.path.join(CLIPPED_DIR, "Aymaraes_Sentinel2_True_color.tif")

print("Calculando NDVI flotante de alta precisión (B08 - B04) / (B08 + B04)...")
with rasterio.open(b04_path) as src_b04, rasterio.open(b08_path) as src_b08:
    b04 = src_b04.read(1).astype(np.float32)
    b08 = src_b08.read(1).astype(np.float32)
    meta = src_b04.meta.copy()
    
    # Máscara donde ambos sean válidos
    valid_mask = (b08 + b04) > 0
    ndvi = np.full_like(b04, np.nan, dtype=np.float32)
    ndvi[valid_mask] = (b08[valid_mask] - b04[valid_mask]) / (b08[valid_mask] + b04[valid_mask])
    
    meta.update({
        "dtype": "float32",
        "nodata": np.nan
    })
    
    ndvi_path = os.path.join(CLIPPED_DIR, "Aymaraes_NDVI_Cientifico_Float32.tif")
    with rasterio.open(ndvi_path, "w", **meta) as dst:
        dst.write(ndvi, 1)
    print(f"  -> Guardado: {ndvi_path}")
    print(f"     NDVI Min={np.nanmin(ndvi):.3f}, Media={np.nanmean(ndvi):.3f}, Max={np.nanmax(ndvi):.3f}")

# Cargar datos para gráfico de verificación
with rasterio.open(rgb_path) as src_rgb:
    rgb = src_rgb.read([1, 2, 3])
    # Normalizar para visualización
    rgb_vis = np.clip(rgb.transpose(1, 2, 0) / 255.0, 0, 1)

with rasterio.open(dem_path) as src_dem:
    dem = src_dem.read(1)
    dem_nodata = src_dem.nodata
    if dem_nodata is not None:
        dem = np.where(dem == dem_nodata, np.nan, dem)
    dem = np.where(dem <= 0, np.nan, dem)

fig, axes = plt.subplots(1, 3, figsize=(18, 7), dpi=300)

# 1. True Color
axes[0].imshow(rgb_vis)
axes[0].set_title("Sentinel-2 L2A: Color Real (RGB)\nProvincia de Aymaraes, Apurímac", fontsize=12, fontweight="bold")
axes[0].axis("off")

# 2. DEM
im_dem = axes[1].imshow(dem, cmap="terrain")
axes[1].set_title("Copernicus DEM GLO-30 (30m)\nTopografía y Relieve", fontsize=12, fontweight="bold")
axes[1].axis("off")
plt.colorbar(im_dem, ax=axes[1], fraction=0.046, pad=0.04, label="Altitud (m s.n.m.)")

# 3. NDVI
im_ndvi = axes[2].imshow(ndvi, cmap="YlGn", vmin=-0.1, vmax=0.8)
axes[2].set_title("NDVI Científico (Sentinel-2 L2A)\nVigor Vegetal y Biomasa", fontsize=12, fontweight="bold")
axes[2].axis("off")
plt.colorbar(im_ndvi, ax=axes[2], fraction=0.046, pad=0.04, label="Índice NDVI")

plt.tight_layout()
preview_path = os.path.join(WORK_DIR, "Aymaraes_Sentinel2_DEM_NDVI_Mosaico.png")
plt.savefig(preview_path, bbox_inches="tight")
plt.close()
print(f"¡Mapa comparativo guardado exitosamente en: {preview_path}!")
