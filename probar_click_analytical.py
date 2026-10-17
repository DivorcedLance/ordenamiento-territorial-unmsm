from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r'C:\Users\divor\Downloads\OT\.chrome_profile', channel='chrome', headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto('https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00:00:00.000Z&toTime=2026-10-15T23:59:59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers')
    page.wait_for_timeout(3000)
    
    # Login si es necesario
    login_btn = page.locator(".confirm-dialog__btn--ok")
    if login_btn.count() > 0 and login_btn.is_visible():
        login_btn.click()
        page.wait_for_url("**/identity.dataspace.copernicus.eu/**", timeout=20000)
        page.fill("input#username", "karina.calluchi@unmsm.edu.pe")
        page.fill("input#password", "K27arina123*castro")
        page.click("input#kc-login, button#kc-login, button[type='submit']")
        page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
        page.wait_for_timeout(4000)
        
    dont_show = page.locator("button:has-text(\"Don't show again\")")
    if dont_show.count() > 0 and dont_show.is_visible():
        dont_show.click()
        page.wait_for_timeout(1000)
        
    # Abrir diálogo de descarga
    page.locator("div[title^='Download image']").first.click()
    page.wait_for_timeout(2000)
    
    # Clic en Analytical
    analytical = page.get_by_text("Analytical", exact=True)
    print("Analytical encontrado:", analytical.count())
    if analytical.count() > 0:
        analytical.first.click()
        page.wait_for_timeout(2000)
        
    page.screenshot(path=r'C:\Users\divor\Downloads\OT\analytical_clicked_check.png')
    print("Screenshot analytical_clicked_check.png guardado.")
