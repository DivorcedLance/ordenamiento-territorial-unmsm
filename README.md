# Ordenamiento Territorial (OT) — UNMSM 2026-II
## Examen Parcial Sustentado: Teledetección Sentinel-2, DEM Copernicus & Geoanálisis (Aymaraes, Apurímac)

Este repositorio contiene el solucionario maestro, scripts de procesamiento satelital automatizado con **Playwright**, cálculo de índices espectrales (**NDVI**, **NDWI**, **EVI**) y modelamiento topográfico con **Copernicus DEM GLO-30** para la **Provincia de Aymaraes (Apurímac)**, correspondiente al Examen Parcial Sustentado del curso de **Ordenamiento Territorial (UNMSM)**.

---

## 📄 Documentos Principales

- **[INSTRUCCIONES_AGENTE_COPERNICUS_OT.md](./INSTRUCCIONES_AGENTE_COPERNICUS_OT.md)**: Manual y protocolo estandarizado para la ejecución autónoma de agentes en otras máquinas (descargas, credenciales, procesamiento y cartografía).
- **[EP SUSTENTADO.docx](./EP%20SUSTENTADO.docx)**: Documento base del Examen Parcial Sustentado (Pregunta 1: Balance Hídrico / Pregunta 2: Biomasa y Holdridge).
- **[EP_Sustentado_Solucionario_Maestro.pdf](./EP_Sustentado_Solucionario_Maestro.pdf)**: Solucionario analítico y teórico en PDF.
- **[Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.png](./Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.png)** / **[.pdf](./Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.pdf)**: Mapa maestro de 4 paneles en alta resolución (Color Real RGB, Topografía DEM GLO-30, NDVI y NDWI).

---

## 🗺️ Delimitación Vectorial Oficial
- `aymaraes_fc.geojson`: GeoJSON de la Provincia de Aymaraes (`FeatureCollection` EPSG:4326).
- `aymaraes_shapefile.zip`: Shapefile oficial comprimido listo para cargar como AOI en Copernicus Browser o QGIS/ArcGIS Pro.

---

## 🛰️ Scripts de Automatización y Procesamiento
- `descargar_mosaico_sentinel2_aymaraes.py`: Descarga y mosaico de bandas Sentinel-2 L2A (10 m) vía Cloud-Optimized GeoTIFFs (COG) y cálculo de NDVI, NDWI y EVI.
- `descargar_y_procesar_dem.py`: Descarga y mosaico automático del Copernicus DEM GLO-30 (30 m).
- `descargar_analitica_completa.py`: Automatización con Playwright (Chrome visible) para interactuar y descargar productos analíticos desde Copernicus Browser.
- `pulir_mapa_maestro.py`: Generación del compendio cartográfico final de 4 paneles.

---

## ☁️ Respaldo en Google Drive
Los archivos raster pesados sin comprimir (> 100 MB cada uno, mosaicos multiespectrales a 10m y teselas originales) están respaldados en la carpeta correspondiente de Google Drive para permitir portabilidad total entre equipos. Todos los productos pueden ser regenerados de forma idéntica ejecutando los scripts incluidos.
