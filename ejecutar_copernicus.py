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
        
        print("Navegando a Copernicus Browser...")
        page.goto(URL, timeout=90000, wait_until="domcontentloaded")
        time.sleep(6)
        
        # 1. Chequear si aparece el modal de bienvenida pidiendo Log in o Use anonymously
        login_modal_btn = page.locator(".rodal button:has-text('Log in')")
        if login_modal_btn.count() > 0 and login_modal_btn.first.is_visible():
            print("Modal de Login detectado en pantalla. Clic en 'Log in'...")
            login_modal_btn.first.click()
            time.sleep(5)
            
        # Si fuimos redirigidos a Keycloak
        if "identity.dataspace.copernicus.eu" in page.url or page.locator("input#username").count() > 0:
            print("En formulario Keycloak. Ingresando usuario y clave...")
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            time.sleep(1)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            print("Esperando retorno a Copernicus Browser...")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            time.sleep(6)
            
        # 2. Si aparece el tutorial / modal "Don't show again"
        dont_show = page.locator("button:has-text(\"Don't show again\")")
        if dont_show.count() > 0 and dont_show.first.is_visible():
            print("Cerrando modal de bienvenida tutorial...")
            dont_show.first.click()
            time.sleep(2)
            
        # Cerrar cualquier otro modal o backdrop
        close_x = page.locator(".rodal-close, .modal-close, button.close")
        if close_x.count() > 0 and close_x.first.is_visible():
            close_x.first.click()
            time.sleep(1)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step3_logged_in.png"))
        print("Captura step3_logged_in.png guardada.")
        
        # 3. Herramienta de Area de Interés (AOI)
        print("Buscando herramienta AOI (Área de Interés)...")
        aoi_btn = page.locator(".aoi-panel-btn-wrapper, [title*='Area of interest'], [title*='area of interest'], [aria-label*='Area of interest']")
        if aoi_btn.count() > 0:
            print("Clic en herramienta AOI...")
            aoi_btn.first.click()
            time.sleep(3)
            page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step4_aoi_panel.png"))
            
            # Buscar opción de subir archivo (Upload)
            upload_input = page.locator("input[type='file']")
            if upload_input.count() > 0:
                print(f"Cargando shapefile/geojson a AOI: {GEOJSON_FILE}")
                upload_input.first.set_input_files(GEOJSON_FILE)
                time.sleep(4)
                page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step5_aoi_uploaded.png"))
            else:
                print("No se encontró input file directo, buscando botón de Upload...")
                upload_btn = page.locator("button:has-text('Upload'), div:has-text('Upload'), .file-upload")
                if upload_btn.count() > 0:
                    upload_btn.first.click()
                    time.sleep(2)
                    upload_input = page.locator("input[type='file']")
                    if upload_input.count() > 0:
                        upload_input.first.set_input_files(GEOJSON_FILE)
                        time.sleep(4)
                        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step5_aoi_uploaded.png"))
                        
        # 4. Herramienta de descarga de imagen
        print("Buscando herramienta de descarga de imagen...")
        download_tool = page.locator(".img-download-btn-wrapper, [title*='Download image']")
        if download_tool.count() > 0:
            print("Clic en descarga de imagen...")
            download_tool.first.click()
            time.sleep(3)
            page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step6_download_modal.png"))
            
            # Ver pestañas del modal de descarga: Analytical, Basic, etc.
            analytical_tab = page.locator("button:has-text('Analytical'), a:has-text('Analytical'), div:has-text('Analytical')")
            if analytical_tab.count() > 0 and analytical_tab.first.is_visible():
                print("Clic en pestaña 'Analytical'...")
                analytical_tab.first.click()
                time.sleep(2)
                page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step7_analytical_tab.png"))

        print("Esperando 10 segundos antes de finalizar para visualizar...")
        time.sleep(10)

if __name__ == "__main__":
    run()
