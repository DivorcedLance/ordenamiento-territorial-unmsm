from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r'C:\Users\divor\Downloads\OT\.chrome_profile', channel='chrome', headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto('https://browser.dataspace.copernicus.eu/?zoom=9&lat=-14.11005&lng=-72.98218&themeId=DEFAULT-THEME&datasetId=S2_L2A_CDAS&fromTime=2026-10-15T00:00:00.000Z&toTime=2026-10-15T23:59:59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=7&dateMode=SINGLE&panel=layers')
    page.wait_for_timeout(4000)
    print("Viewport:", page.viewport_size)
    for el in page.locator("[title]").all():
        t = el.get_attribute('title')
        box = el.bounding_box()
        if box:
            print(f"Title: '{t}', Tag: {el.evaluate('e => e.tagName')}, x={box['x']:.0f}, y={box['y']:.0f}")
