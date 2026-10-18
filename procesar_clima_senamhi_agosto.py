import os
import json
import urllib.request
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import numpy as np
import matplotlib.pyplot as plt

WORK_DIR = r"C:\Users\divor\Downloads\OT"
CLIMA_DIR = os.path.join(WORK_DIR, "clima_senamhi_agosto")
os.makedirs(CLIMA_DIR, exist_ok=True)

# 1. Cargar máscara y geometría oficial de Aymaraes
gdf_aymaraes = gpd.read_file(os.path.join(WORK_DIR, "aymaraes_fc.geojson"))
dem_path = os.path.join(WORK_DIR, "DEM_Aymaraes_Copernicus_30m.tif")

with rasterio.open(dem_path) as s_dem:
    dem_meta = s_dem.meta.copy()
    dem_shape = s_dem.shape
    dem_transform = s_dem.transform
    dem_crs = s_dem.crs
    dem_data = s_dem.read(1)
    dem_mask = dem_data > 0

# Capas oficiales de caracterización climática del SENAMHI (Mes 08 - Agosto)
LAYERS = {
    "precipitacion_agosto": {
        "typename": "g_05_02:05_02_008_03_001_512_0000_00_00",
        "title": "Precipitación Acumulada Agosto (mm)",
        "unit": "mm/mes",
        "cmap": "YlGnBu"
    },
    "temp_minima_agosto": {
        "typename": "g_05_03:05_03_008_03_001_512_0000_00_00",
        "title": "Temperatura Mínima Agosto (°C)",
        "unit": "°C",
        "cmap": "coolwarm"
    },
    "temp_maxima_agosto": {
        "typename": "g_05_04:05_04_008_03_001_512_0000_00_00",
        "title": "Temperatura Máxima Agosto (°C)",
        "unit": "°C",
        "cmap": "plasma"
    }
}

def parse_range_value(rango_str):
    """Extrae el valor medio numérico representativo de rangos como '10 - 15', '-3 - -1', etc."""
    try:
        parts = [p.strip() for p in rango_str.split('-') if p.strip()]
        # Manejo de números negativos
        nums = []
        tokens = rango_str.replace(' ', '').split('-')
        # Limpieza robusta
        if ' - ' in rango_str:
            p1, p2 = rango_str.split(' - ')
            return (float(p1) + float(p2)) / 2.0
        elif len(parts) == 2:
            return (float(parts[0]) + float(parts[1])) / 2.0
    except Exception:
        pass
    return np.nan

rasters_clima = {}

for key, info in LAYERS.items():
    print(f"\nDescargando capa WFS oficial: {info['title']} ({info['typename']})...")
    url_wfs = (
        f"https://idesep.senamhi.gob.pe/geoserver/wfs?SERVICE=WFS&VERSION=1.1.0"
        f"&REQUEST=GetFeature&TYPENAME={info['typename']}"
        f"&BBOX=-14.843,-73.577,-13.804,-72.981,urn:ogc:def:crs:EPSG::4326"
        f"&OUTPUTFORMAT=application/json"
    )
    geojson_out = os.path.join(CLIMA_DIR, f"{key}.geojson")
    
    req = urllib.request.Request(url_wfs, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        with open(geojson_out, "wb") as f:
            f.write(data)
    print(f"  GeoJSON guardado: {geojson_out} ({len(data)/(1024*1024):.2f} MB)")
    
    # Cargar y reproyectar con GeoPandas
    gdf_layer = gpd.read_file(geojson_out)
    gdf_layer = gdf_layer.to_crs(dem_crs)
    # Clip con Aymaraes
    gdf_clip = gpd.clip(gdf_layer, gdf_aymaraes.to_crs(dem_crs))
    
    # Calcular valor numérico medio del rango
    gdf_clip['val_num'] = gdf_clip['rango'].apply(parse_range_value)
    
    # Rasterizar a la misma malla espacial y resolución del DEM de Aymaraes
    shapes = [(geom, val) for geom, val in zip(gdf_clip.geometry, gdf_clip['val_num']) if not np.isnan(val)]
    
    raster_grid = rasterize(
        shapes=shapes,
        out_shape=dem_shape,
        transform=dem_transform,
        fill=-9999.0,
        dtype=np.float32
    )
    raster_grid = np.where(dem_mask & (raster_grid != -9999.0), raster_grid, np.nan)
    
    # Guardar GeoTIFF
    tif_out = os.path.join(CLIMA_DIR, f"Aymaraes_{key}.tif")
    meta_out = dem_meta.copy()
    meta_out.update({"dtype": "float32", "nodata": -9999.0})
    with rasterio.open(tif_out, "w", **meta_out) as dst:
        dst.write(np.where(np.isnan(raster_grid), -9999.0, raster_grid), 1)
    print(f"  GeoTIFF rasterizado: {tif_out}")
    print(f"    Rango: Min={np.nanmin(raster_grid):.2f}, Media={np.nanmean(raster_grid):.2f}, Max={np.nanmax(raster_grid):.2f} {info['unit']}")
    
    rasters_clima[key] = raster_grid

# 2. CÁLCULO DE TEMPERATURA MEDIA Y BIOTEMPERATURA DE HOLDRIDGE (AGOSTO)
print("\n--- Calculando Temperatura Media y Biotemperatura de Holdridge para Agosto ---")
tmin = rasters_clima["temp_minima_agosto"]
tmax = rasters_clima["temp_maxima_agosto"]

# Temperatura media mensual: Tmed = (Tmax + Tmin) / 2
tmed_agosto = (tmax + tmin) / 2.0
tmed_out = os.path.join(CLIMA_DIR, "Aymaraes_temp_media_agosto.tif")
with rasterio.open(tmed_out, "w", **meta_out) as dst:
    dst.write(np.where(np.isnan(tmed_agosto), -9999.0, tmed_agosto), 1)
print(f"Temperatura Media guardada: {tmed_out}")
print(f"  Tmed: Min={np.nanmin(tmed_agosto):.2f}°C, Media={np.nanmean(tmed_agosto):.2f}°C, Max={np.nanmax(tmed_agosto):.2f}°C")

# Biotemperatura de Holdridge mensual:
# Tbio = Tmed si 0 < Tmed <= 30; caso contrario = 0
biotemp_agosto = np.where((tmed_agosto > 0) & (tmed_agosto <= 30), tmed_agosto, 0.0)
biotemp_agosto = np.where(np.isnan(tmed_agosto), np.nan, biotemp_agosto)

biotemp_out = os.path.join(CLIMA_DIR, "Aymaraes_biotemperatura_holdridge_agosto.tif")
with rasterio.open(biotemp_out, "w", **meta_out) as dst:
    dst.write(np.where(np.isnan(biotemp_agosto), -9999.0, biotemp_agosto), 1)
print(f"Biotemperatura Holdridge guardada: {biotemp_out}")
print(f"  Biotemp: Min={np.nanmin(biotemp_agosto):.2f}°C, Media={np.nanmean(biotemp_agosto):.2f}°C, Max={np.nanmax(biotemp_agosto):.2f}°C")

# 3. EXTRAER VALORES PUNTUALES REPRESENTATIVOS PARA CAPITALES DISTRITALES DE AYMARAES
print("\n--- Extrayendo Estadísticas Puntuales en Capitales Distritales ---")
puntos = [
    {"distrito": "Chalhuanca (Capital Provincial)", "lon": -73.242, "lat": -14.296},
    {"distrito": "Cotaruse", "lon": -73.210, "lat": -14.420},
    {"distrito": "Capaya", "lon": -73.340, "lat": -14.070},
    {"distrito": "Toraya", "lon": -73.350, "lat": -13.980},
    {"distrito": "Soraya", "lon": -73.310, "lat": -14.120},
    {"distrito": "Ihuayllo", "lon": -73.370, "lat": -14.040},
    {"distrito": "Tintay", "lon": -73.400, "lat": -13.950}
]

tabla_puntos = []
for p in puntos:
    row, col = rasterio.transform.rowcol(dem_transform, p["lon"], p["lat"])
    # Verificar límites
    if 0 <= row < dem_shape[0] and 0 <= col < dem_shape[1]:
        alt = dem_data[row, col]
        pp = rasters_clima["precipitacion_agosto"][row, col]
        t_min = tmin[row, col]
        t_max = tmax[row, col]
        t_med = tmed_agosto[row, col]
        t_bio = biotemp_agosto[row, col]
        p_info = {
            "Distrito": p["distrito"],
            "Altitud_m": int(alt),
            "Precip_Agosto_mm": round(float(pp), 1) if not np.isnan(pp) else "N/A",
            "Tmin_C": round(float(t_min), 1) if not np.isnan(t_min) else "N/A",
            "Tmax_C": round(float(t_max), 1) if not np.isnan(t_max) else "N/A",
            "Tmed_C": round(float(t_med), 1) if not np.isnan(t_med) else "N/A",
            "Biotemp_C": round(float(t_bio), 1) if not np.isnan(t_bio) else "N/A"
        }
        tabla_puntos.append(p_info)

csv_puntos = os.path.join(CLIMA_DIR, "Aymaraes_Clima_Puntual_Agosto.json")
with open(csv_puntos, "w", encoding="utf-8") as f:
    json.dump(tabla_puntos, f, indent=2, ensure_ascii=False)
print(f"Estadísticas puntuales guardadas en: {csv_puntos}")
for row in tabla_puntos:
    print(f"  {row['Distrito']} ({row['Altitud_m']} msnm): PP={row['Precip_Agosto_mm']} mm | Tmin={row['Tmin_C']}°C | Tmax={row['Tmax_C']}°C | Tmed={row['Tmed_C']}°C | Biotemp={row['Biotemp_C']}°C")

# 4. GENERAR MAPA CARTOGRÁFICO MAESTRO DE CLIMA Y BIOTEMPERATURA (SENAMHI AGOSTO)
print("\nGenerando mapa cartográfico de 4 paneles de Clima y Biotemperatura (Agosto)...")
fig, axes = plt.subplots(2, 2, figsize=(16, 16), dpi=300)

# Panel A: Precipitación Agosto
im_pp = axes[0, 0].imshow(rasters_clima["precipitacion_agosto"], cmap="YlGnBu", vmin=0, vmax=25)
axes[0, 0].set_title("A) Precipitación Acumulada — Agosto (SENAMHI)\nProvincia de Aymaraes (Apurímac)", fontsize=13, fontweight="bold")
axes[0, 0].axis("off")
cb0 = plt.colorbar(im_pp, ax=axes[0, 0], fraction=0.046, pad=0.04)
cb0.set_label("Precipitación (mm/mes)", fontsize=10)

# Panel B: Temperatura Mínima Agosto
im_tmin = axes[0, 1].imshow(tmin, cmap="coolwarm", vmin=-8, vmax=12)
axes[0, 1].set_title("B) Temperatura Mínima Extrema — Agosto (SENAMHI)\nHeladas y Regímenes Térmicos Nocturnos", fontsize=13, fontweight="bold")
axes[0, 1].axis("off")
cb1 = plt.colorbar(im_tmin, ax=axes[0, 1], fraction=0.046, pad=0.04)
cb1.set_label("Temperatura Mínima (°C)", fontsize=10)

# Panel C: Temperatura Máxima Agosto
im_tmax = axes[1, 0].imshow(tmax, cmap="plasma", vmin=12, vmax=26)
axes[1, 0].set_title("C) Temperatura Máxima — Agosto (SENAMHI)\nRadiación Diurna y Balance Térmico", fontsize=13, fontweight="bold")
axes[1, 0].axis("off")
cb2 = plt.colorbar(im_tmax, ax=axes[1, 0], fraction=0.046, pad=0.04)
cb2.set_label("Temperatura Máxima (°C)", fontsize=10)

# Panel D: Biotemperatura de Holdridge (Agosto)
im_bio = axes[1, 1].imshow(biotemp_agosto, cmap="turbo", vmin=0, vmax=18)
axes[1, 1].set_title("D) Biotemperatura de Holdridge — Agosto\nPotencial Biótico y Pisos Ecológicos (Zonas de Vida)", fontsize=13, fontweight="bold")
axes[1, 1].axis("off")
cb3 = plt.colorbar(im_bio, ax=axes[1, 1], fraction=0.046, pad=0.04)
cb3.set_label("Biotemperatura (°C)", fontsize=10)

plt.suptitle("SENAMHI: GRILLAS CLIMÁTICAS Y BIOTEMPERATURA — AGOSTO\nProvincia de Aymaraes (Apurímac) — Ordenamiento Territorial", fontsize=16, fontweight="bold", y=0.98)
plt.tight_layout()

mapa_clima_png = os.path.join(WORK_DIR, "Aymaraes_SENAMHI_Clima_Biotemperatura_Agosto.png")
mapa_clima_pdf = os.path.join(WORK_DIR, "Aymaraes_SENAMHI_Clima_Biotemperatura_Agosto.pdf")
plt.savefig(mapa_clima_png, bbox_inches="tight")
plt.savefig(mapa_clima_pdf, bbox_inches="tight")
plt.close()

print(f"\n¡MAPA CARTOGRÁFICO DE CLIMA Y BIOTEMPERATURA GENERADO EXITOSAMENTE!:")
print(f"  {mapa_clima_png}")
print(f"  {mapa_clima_pdf}")
