from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r'C:\Users\divor\Downloads\OT\.chrome_profile', channel='chrome', headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto('https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00:00:00.000Z&toTime=2026-10-15T23:59:59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers')
    page.wait_for_timeout(4000)
    # Check elements on the right (x > 1200)
    elements = page.locator('*').all()
    print("Elementos en la derecha de la pantalla:")
    for el in elements:
        try:
            box = el.bounding_box()
            if box and box['x'] > 1350 and box['y'] > 50 and box['y'] < 500:
                tag = el.evaluate("e => e.tagName")
                if tag in ['DIV', 'BUTTON', 'A', 'I', 'SPAN']:
                    t = el.get_attribute('title') or ''
                    c = el.get_attribute('class') or ''
                    print(f"Tag: {tag}, x: {box['x']:.0f}, y: {box['y']:.0f}, title: '{t}', class: '{c}'")
        except Exception:
            pass
