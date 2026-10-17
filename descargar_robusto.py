import time
import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\divor\Downloads\OT\.chrome_profile"
DOWNLOAD_DIR = r"C:\Users\divor\Downloads\OT"
SHP_ZIP = os.path.abspath(r"C:\Users\divor\Downloads\OT\aymaraes_shapefile.zip")
GEOJSON = os.path.abspath(r"C:\Users\divor\Downloads\OT\aymaraes_fc.geojson")

URL = "https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00:00:00.000Z&toTime=2026-10-15T23:59:59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"
EMAIL = "karina.calluchi@unmsm.edu.pe"
PASSWORD = "K27arina123*castro"

def run():
    print("Iniciando Playwright...")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            channel="chrome",
            headless=False,
            downloads_path=DOWNLOAD_DIR,
            accept_downloads=True,
            viewport={"width": 1450, "height": 920},
            args=["--start-maximized"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(URL, timeout=90000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        
        # 1. Login
        login_btn = page.locator(".confirm-dialog__btn--ok")
        if login_btn.count() > 0 and login_btn.first.is_visible():
            print("Detectado diálogo inicial. Clic en 'Log in'...")
            login_btn.first.click()
            print("Esperando redirección a Keycloak...")
            page.wait_for_url("**/identity.dataspace.copernicus.eu/**", timeout=30000)
            print("En Keycloak. Rellenando formulario...")
            page.wait_for_selector("input#username", timeout=15000)
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            page.wait_for_timeout(500)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            print("Credenciales enviadas. Esperando retorno a Copernicus Browser...")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            print("Retorno exitoso a Copernicus Browser.")
            
        page.wait_for_timeout(4000)
        
        # Cerrar tutorial "Don't show again" si existe
        dont_show = page.locator("button:has-text(\"Don't show again\")")
        if dont_show.count() > 0 and dont_show.first.is_visible():
            print("Cerrando popup tutorial...")
            dont_show.first.click()
            page.wait_for_timeout(1500)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "login_verified.png"))
        print("Captura login_verified.png guardada.")
        
        # Esperar a que el mapa y la barra lateral de herramientas estén visibles
        print("Esperando barra de herramientas de Copernicus...")
        aoi_tool = page.wait_for_selector(".aoi-panel-btn-wrapper, [title*='Area of interest']", timeout=45000)
        print("Herramienta AOI encontrada. Clic en AOI...")
        aoi_tool.click()
        page.wait_for_timeout(2000)
        
        # Clic en el botón upload de AOI
        upload_icon = page.wait_for_selector("[title*='Upload'], i.fa-upload, .fa-upload", timeout=15000)
        upload_icon.click()
        page.wait_for_timeout(2000)
        
        # En el modal de AOI, subir el archivo zip del shapefile
        print("Buscando input[type='file'] en el modal AOI...")
        file_input = page.wait_for_selector("input[type='file']", timeout=15000)
        print(f"Cargando shapefile: {SHP_ZIP}")
        file_input.set_input_files(SHP_ZIP)
        page.wait_for_timeout(4000)
        
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "aoi_loaded_ok.png"))
        print("Captura aoi_loaded_ok.png guardada.")
        
        # Cerrar el modal de AOI si sigue visible
        close_btn = page.locator(".rodal-close")
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click()
            page.wait_for_timeout(1000)
            
        # Abrir descarga
        print("Abriendo herramienta de Descarga de imagen...")
        dl_tool = page.wait_for_selector(".img-download-btn-wrapper, [title*='Download image']", timeout=15000)
        dl_tool.click()
        page.wait_for_timeout(3000)
        
        # Clic en Analytical
        print("Cambiando a pestaña Analytical...")
        page.locator("button:has-text('Analytical'), a:has-text('Analytical'), div.tab:has-text('Analytical')").first.click()
        page.wait_for_timeout(2000)
        
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "analytical_ready.png"))
        print("Captura analytical_ready.png guardada.")
        
        # Activar Crop to AOI si está
        crop = page.locator("label:has-text('Crop to AOI'), div:has-text('Crop to AOI') input")
        if crop.count() > 0:
            try:
                crop.first.click()
                print("Crop to AOI marcado.")
            except Exception:
                pass
                
        # Marcar NDVI
        ndvi = page.locator("label:has-text('NDVI'), tr:has-text('NDVI') input[type='checkbox']")
        if ndvi.count() > 0:
            try:
                ndvi.first.check()
                print("NDVI marcado.")
            except Exception:
                pass
                
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "before_download.png"))
        
        # Clic en Descargar
        print("Descargando imagen...")
        dl_btn = page.locator("button:has-text('Download'), .btn-download, button.primary:has-text('Download')").first
        with page.expect_download(timeout=120000) as dl_info:
            dl_btn.click()
            print("Esperando generación y descarga en Copernicus...")
        dl = dl_info.value
        target = os.path.join(DOWNLOAD_DIR, dl.suggested_filename)
        dl.save_as(target)
        print(f"¡DESCARGA EXITOSA!: {target}")
        
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "after_download.png"))
        page.wait_for_timeout(5000)

if __name__ == "__main__":
    run()
