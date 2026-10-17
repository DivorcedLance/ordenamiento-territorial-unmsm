import time
import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\divor\Downloads\OT\.chrome_profile"
DOWNLOAD_DIR = r"C:\Users\divor\Downloads\OT"
GEOJSON_FILE = os.path.abspath(r"C:\Users\divor\Downloads\OT\aymaraes_fc.geojson")
SHP_ZIP_FILE = os.path.abspath(r"C:\Users\divor\Downloads\OT\aymaraes_shapefile.zip")

URL = (
    "https://browser.dataspace.copernicus.eu/"
    "?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME"
    "&visualizationUrl=U2FsdGVkX18zjE9dQAlmBO69vPSTsZAmNR0QSrW60NOjB1H0EqCRK%2F0u%2BYDGiy3wF9vMeg9%2BvPvl04BrR5Z3JXbXZlRUKzKR%2B0jjyXznFQBL8yXT3qTyA2GAclHvXiz5"
    "&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00%3A00%3A00.000Z&toTime=2026-10-15T23%3A59%3A59.999Z"
    "&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"
)

EMAIL = "karina.calluchi@unmsm.edu.pe"
PASSWORD = "K27arina123*castro"

def run():
    print("Iniciando Playwright...")
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
        time.sleep(6)
        
        # 1. Login si es necesario
        login_modal_btn = page.locator(".rodal button:has-text('Log in')")
        if login_modal_btn.count() > 0 and login_modal_btn.first.is_visible():
            print("Clic en 'Log in' modal...")
            login_modal_btn.first.click()
            time.sleep(4)
            
        if "identity.dataspace.copernicus.eu" in page.url or page.locator("input#username").count() > 0:
            print("Autenticando en Keycloak...")
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            time.sleep(1)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            time.sleep(6)
            
        # Cerrar posibles popups
        for selector in ["button:has-text(\"Don't show again\")", ".rodal-close", "button.close"]:
            btn = page.locator(selector)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                time.sleep(1)
                
        # 2. Clic en herramienta AOI
        print("Abriendo herramienta AOI...")
        aoi_btn = page.locator(".aoi-panel-btn-wrapper, [title*='Area of interest'], [title*='area of interest']")
        if aoi_btn.count() > 0:
            aoi_btn.first.click()
            time.sleep(2)
            
            # Buscar el botón de Upload (el primer icono en el submenú de AOI)
            print("Buscando botón de Upload en el panel AOI...")
            upload_icon = page.locator(".aoi-panel-btn-wrapper ~ *, [title*='Upload'], [aria-label*='Upload'], i.fa-upload, button:has(.fa-upload)")
            print(f"Iconos upload encontrados: {upload_icon.count()}")
            
            # También podemos escuchar el file chooser de Playwright
            try:
                # Buscar input file oculto en la página
                input_file = page.locator("input[type='file']")
                if input_file.count() > 0:
                    print("Input file encontrado en el DOM! Subiendo aymaraes_fc.geojson...")
                    input_file.first.set_input_files(GEOJSON_FILE)
                    time.sleep(3)
                else:
                    # Clic con file chooser
                    upload_target = page.locator("[title*='Upload'], i.fa-upload, .fa-upload").first
                    with page.expect_file_chooser(timeout=5000) as fc_info:
                        upload_target.click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(GEOJSON_FILE)
                    time.sleep(3)
                print("Shape/GeoJSON cargado exitosamente como AOI!")
            except Exception as e:
                print("Nota sobre carga de archivo:", e)
                
            page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_aoi_set.png"))
            
        # 3. Abrir modal de descarga de imagen
        print("Abriendo diálogo de descarga...")
        download_tool = page.locator(".img-download-btn-wrapper, [title*='Download image']").first
        download_tool.click()
        time.sleep(3)
        
        # 4. Cambiar a la pestaña Analytical
        print("Seleccionando pestaña Analytical...")
        analytical_tab = page.locator(".image-download-tabs button:has-text('Analytical'), button:has-text('Analytical'), a:has-text('Analytical'), div.tab:has-text('Analytical')")
        if analytical_tab.count() > 0:
            analytical_tab.first.click()
            time.sleep(2)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_analytical_panel.png"))
        
        # 5. Configurar opciones analíticas para NDVI y bandas
        print("Configurando opciones analíticas (TIFF, Alta Resolución, Bandas/NDVI)...")
        # Marcar 'Crop to AOI' si está disponible
        crop_toggle = page.locator("label:has-text('Crop to AOI'), div:has-text('Crop to AOI') input, .checkbox:has-text('Crop')")
        if crop_toggle.count() > 0:
            try:
                crop_toggle.first.click()
                print("Opción 'Crop to AOI' activada.")
            except Exception:
                pass
                
        # Seleccionar formato TIFF (16-bit o 32-bit)
        tiff_select = page.locator("select:has-text('TIFF'), select[name*='format']")
        if tiff_select.count() > 0:
            try:
                tiff_select.first.select_option(label="TIFF (raw)")
            except Exception:
                pass
                
        # Marcar NDVI y bandas B04, B08 en las capas analíticas
        layers_to_check = ["NDVI", "B04", "B08", "True color", "Raw bands"]
        for layer_name in layers_to_check:
            cb = page.locator(f"label:has-text('{layer_name}'), tr:has-text('{layer_name}') input[type='checkbox']")
            if cb.count() > 0:
                try:
                    cb.first.check()
                    print(f"Capa/Banda '{layer_name}' seleccionada.")
                except Exception:
                    pass
                    
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_analytical_configured.png"))
        
        # 6. Ejecutar descarga
        print("Haciendo clic en el botón de Descarga...")
        dl_button = page.locator("button:has-text('Download'), .btn-download, button.primary:has-text('Download')").first
        
        try:
            with page.expect_download(timeout=120000) as download_info:
                dl_button.click()
                print("Esperando que comience la descarga...")
            download = download_info.value
            dest_file = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            print(f"Descargando archivo: {download.suggested_filename}...")
            download.save_as(dest_file)
            print(f"¡Descarga completada con éxito en: {dest_file}!")
        except Exception as e:
            print("Resultado de la descarga:", e)
            page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_download_result.png"))

        time.sleep(10)

if __name__ == "__main__":
    run()
