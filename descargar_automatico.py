import time
import os
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\divor\Downloads\OT\.chrome_profile"
DOWNLOAD_DIR = r"C:\Users\divor\Downloads\OT"
GEOJSON_FILE = os.path.abspath(r"C:\Users\divor\Downloads\OT\aymaraes_fc.geojson")
SHP_ZIP_FILE = os.path.abspath(r"C:\Users\divor\Downloads\OT\aymaraes_shapefile.zip")

URL = (
    "https://browser.dataspace.copernicus.eu/"
    "?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME"
    "&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00%3A00%3A00.000Z&toTime=2026-10-15T23%3A59%3A59.999Z"
    "&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"
)

EMAIL = "karina.calluchi@unmsm.edu.pe"
PASSWORD = "K27arina123*castro"

with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
    geojson_data = f.read()

def run():
    print("Iniciando Playwright con Chrome (headless=False)...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=False,
            downloads_path=DOWNLOAD_DIR,
            accept_downloads=True,
            viewport={"width": 1450, "height": 920},
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Cargando Copernicus Browser...")
        page.goto(URL, timeout=90000, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        # 1. Dialog inicial de Login
        login_btn = page.locator(".confirm-dialog__btn--ok, button:has-text('Log in')")
        if login_btn.count() > 0 and login_btn.first.is_visible():
            print("Clic en 'Log in' del diálogo de bienvenida...")
            login_btn.first.click()
            page.wait_for_timeout(4000)
            
        # 2. Formulario Keycloak SSO
        if "identity.dataspace.copernicus.eu" in page.url or page.locator("input#username").count() > 0:
            print("Completando credenciales en Keycloak SSO...")
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            page.wait_for_timeout(1000)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            print("Esperando retorno a Copernicus Browser...")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            page.wait_for_timeout(6000)
            print("Sesión iniciada con éxito.")
            
        # 3. Cerrar tutorial si aparece
        dont_show = page.locator("button:has-text(\"Don't show again\")")
        if dont_show.count() > 0 and dont_show.first.is_visible():
            print("Cerrando modal de bienvenida tutorial...")
            dont_show.first.click()
            page.wait_for_timeout(2000)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot1_ready_map.png"))
        
        # 4. Activar herramienta AOI
        print("Activando herramienta Área de Interés (AOI)...")
        aoi_tool = page.locator(".aoi-panel-btn-wrapper, [title*='Area of interest'], [title*='area of interest']").first
        aoi_tool.click()
        page.wait_for_timeout(2000)
        
        # Abrir modal de upload de AOI (el icono upload en el submenú de AOI)
        upload_icon = page.locator("[title*='Upload'], i.fa-upload, .fa-upload").first
        upload_icon.click()
        page.wait_for_timeout(2000)
        
        # 5. Cargar AOI mediante la pestaña GeoJSON o File drop
        print("Cargando límite de Aymaraes...")
        geojson_tab = page.locator(".rodal div:has-text('GeoJSON'), .rodal button:has-text('GeoJSON'), .rodal a:has-text('GeoJSON')")
        if geojson_tab.count() > 0 and geojson_tab.first.is_visible():
            print("Seleccionando pestaña GeoJSON...")
            geojson_tab.first.click()
            page.wait_for_timeout(1000)
            page.locator(".rodal textarea").first.fill(geojson_data)
            page.wait_for_timeout(1000)
            # Clic en botón de cargar
            load_btn = page.locator(".rodal button:has-text('Load'), .rodal button:has-text('Confirm'), .rodal button:has-text('OK')")
            if load_btn.count() > 0:
                load_btn.first.click()
                page.wait_for_timeout(3000)
                print("Límite cargado vía GeoJSON!")
        else:
            file_input = page.locator(".rodal input[type='file']")
            if file_input.count() > 0:
                print("Subiendo zip shapefile a input file...")
                file_input.first.set_input_files(SHP_ZIP_FILE)
                page.wait_for_timeout(3000)
                print("Límite cargado vía Shapefile zip!")
                
        # Cerrar modal AOI si quedó abierto
        rodal_close = page.locator(".rodal-close")
        if rodal_close.count() > 0 and rodal_close.first.is_visible():
            rodal_close.first.click()
            page.wait_for_timeout(1000)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot2_aoi_configured.png"))
        
        # 6. Abrir herramienta de Descarga de Imagen
        print("Abriendo herramienta de Descarga de Imagen...")
        download_tool = page.locator(".img-download-btn-wrapper, [title*='Download image']").first
        download_tool.click()
        page.wait_for_timeout(3000)
        
        # 7. Cambiar a pestaña Analytical
        print("Seleccionando pestaña Analytical...")
        analytical_tab = page.locator("button:has-text('Analytical'), a:has-text('Analytical'), div.tab:has-text('Analytical')")
        if analytical_tab.count() > 0:
            analytical_tab.first.click()
            page.wait_for_timeout(2000)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot3_analytical_view.png"))
        
        # 8. Activar Crop to AOI
        crop_cb = page.locator("label:has-text('Crop to AOI'), div:has-text('Crop to AOI') input")
        if crop_cb.count() > 0:
            try:
                crop_cb.first.click()
                print("Crop to AOI activado.")
                page.wait_for_timeout(1000)
            except Exception as e:
                print("Aviso Crop to AOI:", e)
                
        # 9. Seleccionar capas analíticas
        # Seleccionar NDVI
        ndvi_cb = page.locator("label:has-text('NDVI'), tr:has-text('NDVI') input[type='checkbox']")
        if ndvi_cb.count() > 0:
            try:
                ndvi_cb.first.check()
                print("Capa NDVI seleccionada.")
            except Exception:
                pass
                
        # Seleccionar B04 y B08
        for band in ["B04", "B08", "True color"]:
            b_cb = page.locator(f"label:has-text('{band}'), tr:has-text('{band}') input[type='checkbox']")
            if b_cb.count() > 0:
                try:
                    b_cb.first.check()
                    print(f"Capa {band} seleccionada.")
                except Exception:
                    pass
                    
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot4_ready_to_download.png"))
        
        # 10. Ejecutar descarga
        print("Iniciando descarga con captura de evento...")
        download_button = page.locator("button:has-text('Download'), .btn-download, button.primary:has-text('Download')").first
        
        try:
            with page.expect_download(timeout=120000) as download_info:
                download_button.click()
                print("Botón de descarga pulsado. Procesando en el servidor Copernicus...")
            download = download_info.value
            dest_file = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            print(f"Descargando archivo: {download.suggested_filename}...")
            download.save_as(dest_file)
            print(f"¡DESCARGA EXITOSA! Guardado en: {dest_file}")
        except Exception as e:
            print("Aviso durante la descarga:", e)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot5_final_state.png"))
        print("Proceso finalizado. Esperando 5 segundos...")
        page.wait_for_timeout(5000)

if __name__ == "__main__":
    run()
