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
    "&visualizationUrl=U2FsdGVkX18zjE9dQAlmBO69vPSTsZAmNR0QSrW60NOjB1H0EqCRK%2F0u%2BYDGiy3wF9vMeg9%2BvPvl04BrR5Z3JXbXZlRUKzKR%2B0jjyXznFQBL8yXT3qTyA2GAclHvXiz5"
    "&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00%3A00%3A00.000Z&toTime=2026-10-15T23%3A59%3A59.999Z"
    "&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"
)

EMAIL = "karina.calluchi@unmsm.edu.pe"
PASSWORD = "K27arina123*castro"

with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
    geojson_str = f.read()

def run():
    print("Iniciando Playwright con persistencia...")
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
        page.goto(URL, timeout=90000, wait_until="domcontentloaded")
        time.sleep(6)
        
        # Login si aplica
        login_modal_btn = page.locator(".rodal button:has-text('Log in')")
        if login_modal_btn.count() > 0 and login_modal_btn.first.is_visible():
            login_modal_btn.first.click()
            time.sleep(4)
        if "identity.dataspace.copernicus.eu" in page.url or page.locator("input#username").count() > 0:
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            time.sleep(1)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            time.sleep(6)
            
        for selector in ["button:has-text(\"Don't show again\")", ".rodal-close", "button.close"]:
            btn = page.locator(selector)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                time.sleep(1)
                
        # 1. Abrir modal AOI
        print("Abriendo herramienta AOI...")
        aoi_btn = page.locator(".aoi-panel-btn-wrapper, [title*='Area of interest']").first
        aoi_btn.click()
        time.sleep(2)
        
        # Clic en el botón upload de la barra superior derecha
        upload_icon = page.locator("[title*='Upload'], i.fa-upload, .fa-upload").first
        upload_icon.click()
        time.sleep(2)
        
        print("Modal 'Define Area of Interest (AOI)' abierto.")
        
        # Intentar cargar vía pestaña GeoJSON o File input
        # Probar pestaña GeoJSON
        geojson_tab = page.locator(".rodal button:has-text('GeoJSON'), .rodal div:has-text('GeoJSON'), .rodal a:has-text('GeoJSON')")
        if geojson_tab.count() > 0 and geojson_tab.first.is_visible():
            print("Clic en pestaña GeoJSON del modal...")
            geojson_tab.first.click()
            time.sleep(1)
            textarea = page.locator(".rodal textarea")
            if textarea.count() > 0:
                print("Pegando GeoJSON en el textarea...")
                textarea.first.fill(geojson_str)
                time.sleep(1)
                # Buscar botón de confirmación
                confirm_btn = page.locator(".rodal button:has-text('Load'), .rodal button:has-text('Confirm'), .rodal button:has-text('OK'), .rodal button:has-text('Upload')")
                if confirm_btn.count() > 0:
                    confirm_btn.first.click()
                    print("Clic en confirmar GeoJSON.")
                    time.sleep(3)
        else:
            # Probar subir archivo zip o geojson
            file_input = page.locator(".rodal input[type='file']")
            if file_input.count() > 0:
                print("Subiendo SHP zip...")
                file_input.first.set_input_files(SHP_ZIP_FILE)
                time.sleep(3)
                
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_aoi_loaded_success.png"))
        print("Captura step_aoi_loaded_success.png guardada.")
        
        # Asegurarse que el modal de AOI esté cerrado si quedó abierto
        modal_close = page.locator(".rodal-close, .modal-close")
        if modal_close.count() > 0 and modal_close.first.is_visible():
            modal_close.first.click()
            time.sleep(1)
            
        # 2. Ahora abrir el modal de descarga de imagen
        print("Abriendo herramienta de Descarga de imagen...")
        download_tool = page.locator(".img-download-btn-wrapper, [title*='Download image']").first
        download_tool.click()
        time.sleep(3)
        
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_download_dialog.png"))
        
        # 3. Pestaña Analytical
        print("Cambiando a pestaña Analytical...")
        analytical_tab = page.locator("button:has-text('Analytical'), a:has-text('Analytical'), div.tab:has-text('Analytical')")
        if analytical_tab.count() > 0:
            analytical_tab.first.click()
            time.sleep(2)
            
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_analytical_dialog.png"))
        
        time.sleep(5)

if __name__ == "__main__":
    run()
