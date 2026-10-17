import time
import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\divor\Downloads\OT\.chrome_profile"
DOWNLOAD_DIR = r"C:\Users\divor\Downloads\OT"

URL = (
    "https://browser.dataspace.copernicus.eu/"
    "?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME"
    "&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00%3A00%3A00.000Z&toTime=2026-10-15T23%3A59%3A59.999Z"
    "&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"
)

EMAIL = "karina.calluchi@unmsm.edu.pe"
PASSWORD = "K27arina123*castro"

def run():
    print("Iniciando descarga analítica de NDVI y Bandas en Copernicus...")
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
        
        # 1. Login si aparece el diálogo
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
            
        # 2. Clic en 'Download image '
        print("Abriendo herramienta de Descarga de imagen...")
        dl_icon = page.locator("div[title^='Download image']").first
        dl_icon.click()
        page.wait_for_timeout(2500)
        
        # 3. Pestaña Analytical
        print("Cambiando a pestaña Analytical...")
        for tab in page.locator(".image-download-tabs button, .image-download-tabs a, button:has-text('Analytical')").all():
            if "analytical" in (tab.text_content() or "").lower():
                tab.click()
                print("Pestaña Analytical seleccionada.")
                page.wait_for_timeout(2000)
                break
                
        # 4. Configurar formato y resolución
        dropdowns = page.locator("select.dropdown").all()
        print(f"Dropdowns encontrados en el modal: {len(dropdowns)}")
        
        # Dropdown 0: Image format (TIFF 16-bit)
        if len(dropdowns) > 0:
            try:
                # Opciones: 'TIFF (16-bit)' o 'image/tiff;depth=16'
                for opt in dropdowns[0].locator("option").all():
                    txt = opt.text_content().strip()
                    if "16-bit" in txt:
                        dropdowns[0].select_option(value=opt.get_attribute("value"))
                        print(f"Formato seleccionado: {txt}")
                        break
            except Exception as e:
                print("Error formato:", e)
                
        # Dropdown 1: Image resolution (HIGH)
        if len(dropdowns) > 1:
            try:
                for opt in dropdowns[1].locator("option").all():
                    txt = opt.text_content().strip()
                    if "HIGH" in txt:
                        dropdowns[1].select_option(value=opt.get_attribute("value"))
                        print(f"Resolución seleccionada: {txt}")
                        break
            except Exception as e:
                print("Error resolución:", e)
                
        # Dropdown 2: Coordinate system (WGS 84 o UTM 18S)
        if len(dropdowns) > 2:
            try:
                for opt in dropdowns[2].locator("option").all():
                    txt = opt.text_content().strip()
                    if "18S" in txt or "WGS 84" in txt:
                        dropdowns[2].select_option(value=opt.get_attribute("value"))
                        print(f"Sistema de coordenadas seleccionado: {txt}")
                        break
            except Exception as e:
                print("Error CRS:", e)
                
        # 5. Seleccionar capas: NDVI, B04, B08, True color
        layers_to_select = ["NDVI", "B04", "B08", "True color", "NDWI"]
        for layer_label in page.locator("label").all():
            txt = (layer_label.text_content() or "").strip()
            if txt in layers_to_select:
                try:
                    # El checkbox asociado
                    cb = layer_label.locator("xpath=preceding-sibling::input[1] | following-sibling::input[1] | input")
                    if cb.count() > 0:
                        cb.first.check()
                        print(f"Capa activada: {txt}")
                    else:
                        layer_label.click()
                        print(f"Label clickeado: {txt}")
                except Exception as e:
                    print(f"Error capa {txt}:", e)
                    
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot_configured_download.png"))
        print("Captura shot_configured_download.png guardada.")
        
        # 6. Ejecutar descarga
        print("Presionando botón Download...")
        dl_button = page.locator("button:has-text('Download'), button.btn-download, button.primary:has-text('Download')").first
        
        try:
            with page.expect_download(timeout=180000) as dl_info:
                dl_button.click()
                print("Solicitud enviada a los servidores de Copernicus. Esperando renderizado y descarga...")
            download = dl_info.value
            target_path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            print(f"Transfiriendo archivo: {download.suggested_filename}...")
            download.save_as(target_path)
            print(f"¡DESCARGA EXITOSA! Archivo guardado en:\n{target_path}")
        except Exception as e:
            print("Aviso de descarga:", e)
            page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot_download_error.png"))
            
        page.wait_for_timeout(5000)

if __name__ == "__main__":
    run()
