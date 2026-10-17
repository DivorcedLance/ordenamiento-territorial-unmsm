from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r'C:\Users\divor\Downloads\OT\.chrome_profile', channel='chrome', headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto('https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00:00:00.000Z&toTime=2026-10-15T23:59:59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers')
    page.wait_for_timeout(3000)
    
    # Abrir download dialog
    page.locator("div[title^='Download image']").first.click()
    page.wait_for_timeout(2000)
    
    # Inspect elements with text 'Analytical' or 'Download'
    for el in page.locator("*").all():
        t = (el.text_content() or "").strip()
        if t in ['Analytical', 'Basic', 'High-res print', 'Download']:
            box = el.bounding_box()
            tag = el.evaluate("e => e.tagName")
            cls = el.get_attribute("class") or ""
            print(f"Tag: {tag}, Text: '{t}', Class: '{cls}', Box: {box}")
