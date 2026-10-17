from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\divor\Downloads\OT\.chrome_profile"
URL = "https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00:00:00.000Z&toTime=2026-10-15T23:59:59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(USER_DATA_DIR, channel="chrome", headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(4000)
    
    # Abrir AOI y upload
    aoi = page.locator(".aoi-panel-btn-wrapper, [title*='Area of interest']").first
    if aoi.count() > 0:
        aoi.click()
        page.wait_for_timeout(1500)
        up = page.locator("[title*='Upload'], i.fa-upload, .fa-upload").first
        if up.count() > 0:
            up.click()
            page.wait_for_timeout(1500)
            
    # Listar elementos dentro de .rodal
    print("Elementos en modal rodal:")
    for el in page.locator(".rodal *").all():
        t = (el.text_content() or "").strip()
        tag = el.evaluate("e => e.tagName")
        cls = el.get_attribute("class") or ""
        if tag in ["INPUT", "BUTTON", "A", "TEXTAREA", "DIV"] and len(t) < 40 and t:
            print(f"Tag: {tag}, Class: {cls}, Text: '{t}'")
