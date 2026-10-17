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

with open(GEOJSON, "r", encoding="utf-8") as f:
    geojson_text = f.read()

def run():
    print("Iniciando Playwright paso a paso...")
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
        page.goto(URL, timeout=90000)
        page.wait_for_timeout(4000)
        
        # 1. Login inicial
        print("Verificando si requiere login...")
        login_btn = page.locator(".confirm-dialog__btn--ok")
        if login_btn.count() > 0 and login_btn.first.is_visible():
            print("Clic en 'Log in' del diálogo...")
            login_btn.first.click()
            page.wait_for_timeout(2000)
            
        if "identity.dataspace.copernicus.eu" in page.url or page.locator("input#username").count() > 0:
            print("Llenando credenciales en Keycloak...")
            page.wait_for_selector("input#username", timeout=15000)
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            print("Esperando regreso a Copernicus Browser...")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            page.wait_for_timeout(5000)
            
        # Cerrar tutorial si existe
        dont_show = page.locator("button:has-text(\"Don't show again\")")
        if dont_show.count() > 0 and dont_show.first.is_visible():
            dont_show.first.click()
            page.wait_for_timeout(1000)
            
        # 2. Clic en 'Create an area of interest'
        print("Clic en 'Create an area of interest'...")
        aoi_btn = page.locator("div[title^='Create an area of interest']").first
        aoi_btn.click()
        page.wait_for_timeout(2000)
        
        # Listar nuevos títulos o botones que hayan aparecido
        print("Títulos visibles tras abrir AOI:")
        for el in page.locator("[title]").all():
            t = el.get_attribute("title")
            if any(k in t.lower() for k in ["upload", "draw", "polygon", "rectangle"]):
                print(f"  -> Title: '{t}'")
                
        # Clic en upload de AOI
        up_btn = page.locator("div[title*='Upload'], div[title*='upload'], [title*='Upload']").first
        if up_btn.count() > 0:
            print(f"Clic en '{up_btn.get_attribute('title')}'...")
            up_btn.click()
            page.wait_for_timeout(2000)
            
        # Modal 'Define Area of Interest (AOI)'
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_modal_aoi.png"))
        print("Captura step_modal_aoi.png guardada.")
        
        # Subir archivo al input file
        print("Buscando input file...")
        file_input = page.locator(".rodal input[type='file'], input[type='file']")
        if file_input.count() > 0:
            print("Cargando aymaraes_shapefile.zip al input file...")
            file_input.first.set_input_files(SHP_ZIP)
            page.wait_for_timeout(4000)
        else:
            print("No se encontró input file directo, revisando pestaña GeoJSON...")
            for tab in page.locator(".rodal div, .rodal span, .rodal button").all():
                if (tab.text_content() or "").strip() == "GeoJSON":
                    tab.click()
                    page.wait_for_timeout(1000)
                    page.locator(".rodal textarea").fill(geojson_text)
                    page.wait_for_timeout(1000)
                    page.locator(".rodal button:has-text('Load'), .rodal button:has-text('Confirm')").click()
                    page.wait_for_timeout(3000)
                    break
                    
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_aoi_applied.png"))
        print("Captura step_aoi_applied.png guardada.")
        
        # Cerrar modal AOI si quedó abierto
        rodal_close = page.locator(".rodal-close")
        if rodal_close.count() > 0 and rodal_close.first.is_visible():
            rodal_close.first.click()
            page.wait_for_timeout(1000)
            
        # 3. Descarga de imagen
        print("Clic en 'Download image '...")
        dl_icon = page.locator("div[title^='Download image']").first
        dl_icon.click()
        page.wait_for_timeout(3000)
        
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_dl_modal.png"))
        print("Captura step_dl_modal.png guardada.")
        
        # Cambiar a Analytical
        print("Cambiando a pestaña Analytical...")
        for tab in page.locator("button, a, div").all():
            if (tab.text_content() or "").strip() == "Analytical":
                tab.click()
                print("Pestaña Analytical seleccionada.")
                page.wait_for_timeout(2000)
                break
                
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step_analytical_modal.png"))
        print("Captura step_analytical_modal.png guardada.")
        
        # Listar opciones en el modal Analytical
        print("Elementos en modal Analytical:")
        for el in page.locator(".rodal input, .rodal select, .rodal label, div[class*='download'] input, div[class*='download'] select").all():
            t = (el.text_content() or "").strip()
            val = el.get_attribute("value") or ""
            cls = el.get_attribute("class") or ""
            tag = el.evaluate("e => e.tagName")
            if t or val:
                print(f"  [{tag}] text='{t}', val='{val}', class='{cls}'")
                
        page.wait_for_timeout(10000)

if __name__ == "__main__":
    run()
