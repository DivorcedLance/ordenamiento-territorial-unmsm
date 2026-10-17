# 🛰️ INSTRUCCIONES TÉCNICAS Y PROTOCOLO PARA EL AGENTE DE ORDENAMIENTO TERRITORIAL (OT)
**Curso:** Ordenamiento Territorial (UNMSM)  
**Tema:** Examen Parcial Sustentado (Balance Hídrico Actual/Potencial, Biomasa, NDVI, NDWI, EVI, DEM y Holdridge)  
**Área de Intervención:** Provincia de Aymaraes, Departamento de Apurímac, Perú (UBIGEO 0304).

---

## 📌 1. REGLA FUNDAMENTAL DE SEGURIDAD Y CREDENCIALES
> [!IMPORTANT]
> **SOLICITUD OBLIGATORIA DE CREDENCIALES:**
> El agente **NUNCA** debe asumir, inventar ni hardcodear credenciales en el código fuente de repositorios públicos.
> Al iniciar la tarea de descarga o interacción con el ecosistema de **Copernicus Data Space Ecosystem (CDSE)** / **Copernicus Browser**, el agente **DEBE SOLICITAR EXPLÍCITAMENTE AL USUARIO** sus credenciales de acceso:
> 1. **Correo electrónico institucional o personal registrado en Copernicus.**
> 2. **Contraseña de acceso a Copernicus Data Space Ecosystem.**
>
> **Ejemplo de solicitud al usuario:**
> *"Para proceder con la descarga automatizada de bandas multiespectrales Sentinel-2 desde Copernicus Browser mediante Playwright, por favor proporcióneme sus credenciales de Copernicus Data Space Ecosystem (Correo electrónico y contraseña)."*

---

## 🗺️ 2. CONTEXTO Y DELIMITACIÓN DEL ÁREA DE ESTUDIO
1. **Unidad Territorial:** Provincia de **Aymaraes** (Capital: Chalhuanca, Apurímac).
2. **Coordenadas y Bounding Box:**
   - Longitud: `[-73.577° W, -72.981° W]`
   - Latitud: `[-14.843° S, -13.804° S]`
   - Proyección cartográfica óptima: **UTM Zona 18S (EPSG:32718)** / Geográficas **WGS 84 (EPSG:4326)**.
3. **Archivos de Delimitación Vectorial Incluidos en la Carpeta:**
   - `aymaraes_fc.geojson`: GeoJSON oficial tipo `FeatureCollection`.
   - `aymaraes_shapefile.zip`: Shapefile oficial comprimido listo para subir directamente como Área de Interés (AOI) a Copernicus Browser.

---

## 🚀 3. PROCEDIMIENTO PASO A PASO PARA EL AGENTE

### Paso 1: Configuración del Entorno Python
Si estás en una nueva máquina, asegúrate de instalar las dependencias:
```bash
pip install -r requirements.txt
playwright install chromium
```
Librerías principales requeridas: `playwright`, `rasterio`, `geopandas`, `shapely`, `matplotlib`, `numpy`, `scipy`.

---

### Paso 2: Descarga Automatizada con Copernicus Browser (Playwright)
Para descargar productos visualizados directamente desde Copernicus Browser con interfaz de usuario visible:
1. Usar siempre `headless=False` y preferiblemente `channel="chrome"` con un perfil aislado:
   ```python
   context = p.chromium.launch_persistent_context(
       user_data_dir="./.chrome_profile",
       channel="chrome",
       headless=False,
       downloads_path="./",
       accept_downloads=True,
       args=["--start-maximized"]
   )
   ```
2. **Flujo de Navegación y Autenticación:**
   - Navegar a la URL del área de interés:
     `https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&datasetId=S2_L2A_CDAS`
   - Si aparece el diálogo modal de bienvenida (`.confirm-dialog__btn--ok`), hacer clic en **"Log in"**.
   - Ingresar el usuario y contraseña provistos por el usuario en el formulario Keycloak SSO (`https://identity.dataspace.copernicus.eu/`).
   - Esperar la redirección de vuelta a Copernicus Browser.
   - Cerrar el tutorial inicial ("Don't show again").
3. **Carga del Área de Interés (AOI):**
   - Clic en la herramienta *Área de Interés* (`div[title^='Create an area of interest']`).
   - Clic en el botón *Upload* del submenú superior derecho.
   - En el modal emergente, cargar el archivo `aymaraes_shapefile.zip` o pegar el GeoJSON en la pestaña *GeoJSON*.
4. **Descarga Analítica:**
   - Clic en el icono de *Descarga de imagen* (`div[title^='Download image']`).
   - Cambiar a la pestaña **Analytical**.
   - Configurar los parámetros:
     - Formato de Imagen: **TIFF (16-bit)** o **TIFF (32-bit float)**.
     - Resolución: **HIGH** (10 metros nativos).
     - Sistema de Coordenadas: **WGS 84 (EPSG:4326)** o **UTM 18S (EPSG:32718)**.
     - Capas activadas: `NDVI`, `NDWI`, `B04` (Rojo), `B08` (NIR), `B03` (Verde), `B02` (Azul) y `True color` (RGB).
   - Presionar el botón verde **Download** y capturar el evento de descarga con `page.expect_download()`.

---

### Paso 3: Descarga y Procesamiento del Modelo Digital de Elevación (DEM 30m)
El archivo `descargar_y_procesar_dem.py` automatiza la descarga gratuita del **Copernicus DEM GLO-30** (30 metros de resolución espacial) sin requerir credenciales:
- Descarga las 4 teselas que cubren Aymaraes desde el bucket público de AWS S3:
  `Copernicus_DSM_COG_10_S14_00_W073_00_DEM`  
  `Copernicus_DSM_COG_10_S14_00_W074_00_DEM`  
  `Copernicus_DSM_COG_10_S15_00_W073_00_DEM`  
  `Copernicus_DSM_COG_10_S15_00_W074_00_DEM`  
- Genera el mosaico regional y lo recorta con `aymaraes_fc.geojson` produciendo:
  `DEM_Aymaraes_Copernicus_30m.tif` (Elevaciones entre 1,950 m s.n.m. y 5,160 m s.n.m.).

---

### Paso 4: Descarga del Mosaico Sentinel-2 L2A y Cálculo de Índices
El script `descargar_mosaico_sentinel2_aymaraes.py` realiza la descarga directa de las bandas reflectivas de superficie (BOA) a 10m vía streaming Cloud-Optimized GeoTIFF (COG) para las 4 teselas de la fecha óptima sin nubosidad (`S2A_T18LXK`, `S2A_T18LYK`, `S2A_T18LXJ`, `S2A_T18LYJ`):
1. **Cálculo de NDVI (Normalized Difference Vegetation Index):**
   $$\text{NDVI} = \frac{\text{B08 (NIR)} - \text{B04 (Red)}}{\text{B08} + \text{B04}}$$
2. **Cálculo de NDWI (Normalized Difference Water Index - McFeeters):**
   $$\text{NDWI} = \frac{\text{B03 (Green)} - \text{B08 (NIR)}}{\text{B03} + \text{B08}}$$
3. **Cálculo de EVI (Enhanced Vegetation Index):**
   $$\text{EVI} = 2.5 \times \frac{\text{B08} - \text{B04}}{\text{B08} + 6.0 \times \text{B04} - 7.5 \times \text{B02} + 1.0}$$

---

### Paso 5: Generación del Compendio Cartográfico Maestro
El script `pulir_mapa_maestro.py` genera la infografía comparativa cuádruple:
- **Panel A:** Color Real Sentinel-2 (RGB 10m) con fondo transparente/blanco limpio.
- **Panel B:** Relieve y Topografía 3D (Copernicus DEM GLO-30m).
- **Panel C:** NDVI Científico (Vigor vegetal y biomasa).
- **Panel D:** NDWI (Balance hídrico, red fluvial y humedad del suelo).
- Salidas producidas:
  - `Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.png` (300 DPI)
  - `Aymaraes_Sentinel2_DEM_NDVI_NDWI_Maestro.pdf` (Vectorial listo para informe)

---

## 📝 4. RESOLUCIÓN DE LAS 2 PREGUNTAS DEL EXAMEN PARCIAL
Los mapas y rasters procesados alimentan las dos preguntas del archivo `EP SUSTENTADO.docx`:

### Pregunta 1: Balance Hídrico Actual y Potencial
- **Insumos:** `Aymaraes_NDWI_10m.tif`, `Aymaraes_NDVI_10m.tif` (para derivar el coeficiente de cultivo $K_c = 1.25 \times \text{NDVI} + 0.1$), y `DEM_Aymaraes_Copernicus_30m.tif`.
- **Enfoque conceptual:** Capacidad de carga e infraestructura noosférica (Vernadsky - LaRouche).
- **Modelamiento:** Utilizar el DEM para determinar las microcuencas colectoras y áreas de siembra y cosecha de agua (qochas altoandinas en altitudes $> 4200$ m, zanjas de infiltración y represamiento de cabeceras).

### Pregunta 2: Biomasa Actual y Potencial Biótico (Holdridge)
- **Insumos:** `Aymaraes_NDVI_10m.tif`, `Aymaraes_EVI_10m.tif`, y el gradiente altitudinal del DEM.
- **Enfoque conceptual:** Estimación de biomasa seca ($t/\text{ha}$) acoplando la matriz bioclimática de Zonas de Vida de Holdridge (desde Páramo muy húmedo subalpino en las cumbres hasta Matorral desértico y Estepa espinosa en el cañón del río Chalhuanca).
- **Cálculo de biomasa:**
  $$\text{Biomasa Actual (t MS/ha)} = a \times \exp(b \times \text{NDVI})$$
  Comparada contra la capacidad de soporte potencial del ecosistema bajo intervención antrópica organizada.

---

## 📦 5. NOTA SOBRE ARCHIVOS PESADOS Y GOOGLE DRIVE
> [!NOTE]
> Los archivos raster GeoTIFF de alta resolución a 10m sin comprimir (`productos_aymaraes_finales/*.tif` y mosaicos de más de 100MB) son almacenados y respaldados en la carpeta compartida de **Google Drive** para evitar exceder las restricciones de tamaño de GitHub. En el repositorio de GitHub se preservan todos los scripts reproducibles, vectoriales, mapas generados y documentos del examen.
