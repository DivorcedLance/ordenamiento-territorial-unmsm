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

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(USER_DATA_DIR, channel="chrome", headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(4000)
    
    # 1. Login
    login_btn = page.locator(".confirm-dialog__btn--ok")
    if login_btn.count() > 0 and login_btn.is_visible():
        print("Logging in...")
        login_btn.click()
        page.wait_for_timeout(3000)
        if "identity.dataspace.copernicus.eu" in page.url or page.locator("input#username").count() > 0:
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            page.click("input#kc-login, button#kc-login, button[type='submit']")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            page.wait_for_timeout(5000)
            
    # Cerrar tutorial si aparece
    dont_show = page.locator("button:has-text(\"Don't show again\")")
    if dont_show.count() > 0 and dont_show.is_visible():
        dont_show.click()
        page.wait_for_timeout(1000)
        
    # 2. AOI
    print("Abriendo AOI...")
    page.locator(".aoi-panel-btn-wrapper, [title*='Area of interest']").first.click()
    page.wait_for_timeout(1500)
    
    # Upload icon
    page.locator("[title*='Upload'], i.fa-upload, .fa-upload").first.click()
    page.wait_for_timeout(1500)
    
    # Inspeccionar elementos dentro del modal AOI
    print("Buscando input file dentro de modal...")
    file_input = page.locator(".rodal input[type='file'], input[type='file']")
    print(f"Inputs file encontrados: {file_input.count()}")
    if file_input.count() > 0:
        print("Cargando aymaraes_shapefile.zip al input file...")
        file_input.first.set_input_files(SHP_ZIP)
        page.wait_for_timeout(3000)
    
    # Tomar captura
    page.screenshot(path=os.path.join(DOWNLOAD_DIR, "test_upload_aoi.png"))
    print("Captura guardada: test_upload_aoi.png")
