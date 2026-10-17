import time
import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\divor\Downloads\OT\.chrome_profile"
DOWNLOAD_DIR = r"C:\Users\divor\Downloads\OT"

URL = (
    "https://browser.dataspace.copernicus.eu/"
    "?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME"
    "&visualizationUrl=U2FsdGVkX18zjE9dQAlmBO69vPSTsZAmNR0QSrW60NOjB1H0EqCRK%2F0u%2BYDGiy3wF9vMeg9%2BvPvl04BrR5Z3JXbXZlRUKzKR%2B0jjyXznFQBL8yXT3qTyA2GAclHvXiz5"
    "&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00%3A00%3A00.000Z&toTime=2026-10-15T23%3A59%3A59.999Z"
    "&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"
)

def run():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=False,
            downloads_path=DOWNLOAD_DIR,
            accept_downloads=True,
            viewport={"width": 1400, "height": 900},
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(URL, timeout=60000, wait_until="domcontentloaded")
        time.sleep(5)
        
        # 1. Cerrar popup de bienvenida
        print("Buscando modal de bienvenida...")
        dont_show = page.locator("button:has-text(\"Don't show again\"), button:has-text('Cerrar'), .modal-close, button.close")
        if dont_show.count() > 0 and dont_show.first.is_visible():
            print("Cerrando modal de bienvenida...")
            dont_show.first.click()
            time.sleep(2)
        
        # 2. Guardar captura sin modal
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step1_clean_view.png"))
        
        # 3. Buscar botones de descarga en la barra lateral derecha
        # El icono de descarga de imagen suele tener clase fa-download, fa-camera, o title 'Download Image'
        print("Buscando herramientas de descarga...")
        download_tool = page.locator("[title*='Download'], [aria-label*='Download'], button:has(.fa-download), .download-button")
        for i in range(download_tool.count()):
            elem = download_tool.nth(i)
            print(f"Tool {i}: tag={elem.evaluate('e => e.tagName')}, title={elem.get_attribute('title')}, class={elem.get_attribute('class')}")
        
        # Si existe, hacer clic en el botón de descarga
        if download_tool.count() > 0:
            print("Haciendo clic en la herramienta de descarga...")
            download_tool.first.click()
            time.sleep(3)
            page.screenshot(path=os.path.join(DOWNLOAD_DIR, "step2_download_panel.png"))
            
        time.sleep(5)

if __name__ == "__main__":
    run()
