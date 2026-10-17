import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt

WORK_DIR = r"C:\Users\divor\Downloads\OT"
OUT_DIR = os.path.join(WORK_DIR, "productos_aymaraes_finales")

dem_path = os.path.join(WORK_DIR, "DEM_Aymaraes_Copernicus_30m.tif")
tci_path = os.path.join(OUT_DIR, "Aymaraes_Sentinel2_TCI.tif")
ndvi_path = os.path.join(OUT_DIR, "Aymaraes_NDVI_10m.tif")
ndwi_path = os.path.join(OUT_DIR, "Aymaraes_NDWI_10m.tif")

with rasterio.open(dem_path) as s_dem:
    dem_raw = s_dem.read(1)
    dem_val = np.where(dem_raw > 0, dem_raw, np.nan)

with rasterio.open(tci_path) as s_vis:
    vis_r = s_vis.read([1, 2, 3]).astype(np.float32)
    # Crear fondo blanco para los píxeles nodata (0, 0, 0)
    nodata_mask = (vis_r[0] == 0) & (vis_r[1] == 0) & (vis_r[2] == 0)
    vis_rgb = np.clip(vis_r.transpose(1, 2, 0) / 255.0, 0, 1)
    vis_rgb[nodata_mask] = 1.0  # Fondo blanco limpio

with rasterio.open(ndvi_path) as s_ndvi:
    ndvi_raw = s_ndvi.read(1)
    ndvi_val = np.where(ndvi_raw != -9999.0, ndvi_raw, np.nan)

with rasterio.open(ndwi_path) as s_ndwi:
    ndwi_raw = s_ndwi.read(1)
    ndwi_val = np.where(ndwi_raw != -9999.0, ndwi_raw, np.nan)

fig, axes = plt.subplots(2, 2, figsize=(16, 16), dpi=300)

# Panel A: True Color RGB
axes[0, 0].imshow(vis_rgb)
axes[0, 0].set_title("A) Sentinel-2 L2A: Color Real (RGB 10m)\nProvincia de Aymaraes (Apurímac)", fontsize=13, fontweight="bold")
axes[0, 0].axis("off")

# Panel B: Copernicus DEM GLO-30
im_dem = axes[0, 1].imshow(dem_val, cmap="terrain")
axes[0, 1].set_title("B) Copernicus DEM GLO-30 (30m)\nTopografía, Relieve y Cuencas Hidrográficas", fontsize=13, fontweight="bold")
axes[0, 1].axis("off")
cb1 = plt.colorbar(im_dem, ax=axes[0, 1], fraction=0.046, pad=0.04)
cb1.set_label("Altitud (m s.n.m.)", fontsize=10)

# Panel C: NDVI 10m
im_ndvi = axes[1, 0].imshow(ndvi_val, cmap="YlGn", vmin=-0.05, vmax=0.75)
axes[1, 0].set_title("C) NDVI Científico 10m (Sentinel-2 L2A)\nVigor Vegetal y Potencial Biótico (Holdridge)", fontsize=13, fontweight="bold")
axes[1, 0].axis("off")
cb2 = plt.colorbar(im_ndvi, ax=axes[1, 0], fraction=0.046, pad=0.04)
cb2.set_label("NDVI", fontsize=10)

# Panel D: NDWI 10m
im_ndwi = axes[1, 1].imshow(ndwi_val, cmap="BrBG", vmin=-0.5, vmax=0.3)
axes[1, 1].set_title("D) NDWI 10m (Sentinel-2 L2A)\nBalance Hídrico, Humedad del Suelo y Red Fluvial", fontsize=13, fontweight="bold")
axes[1, 1].axis("off")
cb3 = plt.colorbar(im_ndwi, ax=axes[1, 1], fraction=0.046, pad=0.04)
cb3.set_label("NDWI", fontsize=10)

plt.suptitle("COMPENDIO CARTOGRÁFICO MAESTRO: AYMARAES (APURÍMAC)\nSentinel-2 L2A (10m) + Copernicus DEM GLO-30 (30m) — Ordenamiento Territorial", fontsize=16, fontweight="bold", y=0.98)
plt.tight_layout()

final_png = os.path.join(WORK_DIR, "Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.png")
final_pdf = os.path.join(WORK_DIR, "Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.pdf")

plt.savefig(final_png, bbox_inches="tight")
plt.savefig(final_pdf, bbox_inches="tight")
plt.close()

print(f"Mapas guardados exitosamente:\n  {final_png}\n  {final_pdf}")
