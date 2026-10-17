import time
import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\divor\Downloads\OT\.chrome_profile"
DOWNLOAD_DIR = r"C:\Users\divor\Downloads\OT"

URL = "https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00:00:00.000Z&toTime=2026-10-15T23:59:59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"
EMAIL = "karina.calluchi@unmsm.edu.pe"
PASSWORD = "K27arina123*castro"

def run():
    print("Iniciando descarga analítica completa en Copernicus...")
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
        page.wait_for_timeout(3500)
        
        # 1. Login si es necesario
        login_btn = page.locator(".confirm-dialog__btn--ok")
        if login_btn.count() > 0 and login_btn.is_visible():
            login_btn.click()
            page.wait_for_url("**/identity.dataspace.copernicus.eu/**", timeout=20000)
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            page.wait_for_timeout(4000)
            
        dont_show = page.locator("button:has-text(\"Don't show again\")")
        if dont_show.count() > 0 and dont_show.is_visible():
            dont_show.click()
            page.wait_for_timeout(1000)
            
        # 2. Abrir modal de descarga
        print("Abriendo diálogo de descarga...")
        page.locator("div[title^='Download image']").first.click()
        page.wait_for_timeout(2000)
        
        # 3. Pestaña Analytical
        print("Cambiando a pestaña Analytical...")
        page.get_by_text("Analytical", exact=True).click()
        page.wait_for_timeout(1500)
        
        # 4. Configurar selects
        selects = page.locator(".analytical-mode select, select.dropdown").all()
        print(f"Selects disponibles: {len(selects)}")
        
        # Select 0: Formato -> TIFF (16-bit)
        if len(selects) > 0:
            for opt in selects[0].locator("option").all():
                if "16-bit" in (opt.text_content() or ""):
                    selects[0].select_option(value=opt.get_attribute("value"))
                    print("Formato configurado: TIFF (16-bit)")
                    break
                    
        # Select 1: Resolución -> HIGH
        if len(selects) > 1:
            for opt in selects[1].locator("option").all():
                if "HIGH" in (opt.text_content() or ""):
                    selects[1].select_option(value=opt.get_attribute("value"))
                    print("Resolución configurada: HIGH")
                    break
                    
        # 5. Marcar checkboxes: NDVI, B04, B08, True color, NDWI
        target_layers = ["NDVI", "B04", "B08", "True color", "NDWI"]
        for lbl in page.locator("label").all():
            txt = (lbl.text_content() or "").strip()
            if txt in target_layers:
                try:
                    # Buscar el input checkbox correspondiente
                    cb = lbl.locator("xpath=preceding-sibling::input[1] | following-sibling::input[1] | input")
                    if cb.count() > 0:
                        cb.first.check()
                        print(f"Checkbox activado: {txt}")
                    else:
                        lbl.click()
                        print(f"Label clickeado: {txt}")
                except Exception as e:
                    print(f"Error activando {txt}:", e)
                    
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "shot_before_click_download.png"))
        print("Captura shot_before_click_download.png guardada.")
        
        # 6. Clic en el botón verde Download
        print("Buscando botón verde Download...")
        # En el header del modal, buscar el elemento con texto 'Download'
        dl_btn = page.locator("a:has-text('Download'), button:has-text('Download'), div:has-text('Download')").filter(has_text="Download")
        # El botón de descarga es el que tiene la clase btn o está dentro del header
        download_target = None
        for i in range(dl_btn.count()):
            b = dl_btn.nth(i).bounding_box()
            if b and b['y'] < 120 and b['x'] > 500:
                download_target = dl_btn.nth(i)
                print(f"Botón de descarga detectado en x={b['x']:.0f}, y={b['y']:.0f}")
                break
                
        if download_target is None:
            # Fallback por coordenadas
            print("Usando coordenadas del botón Download...")
            page.mouse.click(688, 85)
        else:
            with page.expect_download(timeout=180000) as download_info:
                download_target.click()
                print("Esperando inicio de la descarga...")
            dl = download_info.value
            out_name = os.path.join(DOWNLOAD_DIR, dl.suggested_filename)
            print(f"Descargando: {dl.suggested_filename}...")
            dl.save_as(out_name)
            print(f"¡DESCARGA COMPLETADA CON ÉXITO!: {out_name}")
            
        page.wait_for_timeout(5000)

if __name__ == "__main__":
    run()
