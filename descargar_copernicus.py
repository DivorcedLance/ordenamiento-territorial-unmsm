import time
import os
import sys
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

EMAIL = "karina.calluchi@unmsm.edu.pe"
PASSWORD = "K27arina123*castro"

def run():
    print("Iniciando Playwright con Chrome (headless=False)...")
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
        
        print(f"Navegando a Copernicus Browser: {URL}")
        page.goto(URL, timeout=60000, wait_until="domcontentloaded")
        time.sleep(5)
        
        # Buscar botón de Login
        print("Verificando estado de sesión...")
        # En Copernicus Browser el login suele estar en la barra superior o lateral
        login_btn = page.locator("button:has-text('Login'), a:has-text('Login'), button:has-text('Log in'), a:has-text('Log in'), [data-testid='login-button']")
        
        if login_btn.count() > 0 and login_btn.first.is_visible():
            print("Botón de Login encontrado, haciendo clic...")
            login_btn.first.click()
            time.sleep(4)
        else:
            # Buscar icono de usuario o botón en el sidebar
            user_btn = page.locator("i.fa-user, [title*='Login'], [aria-label*='Login'], .user-icon, button:has(.fa-user)")
            if user_btn.count() > 0 and user_btn.first.is_visible():
                print("Haciendo clic en icono de usuario...")
                user_btn.first.click()
                time.sleep(4)
        
        # Verificar si estamos en la página de login de Keycloak
        print(f"URL actual: {page.url}")
        if "identity.dataspace.copernicus.eu" in page.url or page.locator("input#username").count() > 0:
            print("Página de autenticación detectada. Ingresando credenciales...")
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            time.sleep(1)
            # Submit
            submit_btn = page.locator("input#kc-login, button#kc-login, button[type='submit']")
            submit_btn.click()
            print("Credenciales enviadas. Esperando redirección...")
            page.wait_for_url("**/browser.dataspace.copernicus.eu/**", timeout=60000)
            time.sleep(5)
            print("Login completado con éxito.")
        else:
            print("Ya autenticado o login inline.")
            
        print("Página lista. URL actual:", page.url)
        time.sleep(5)
        
        # Guardar captura de pantalla del estado actual
        screenshot_path = os.path.join(DOWNLOAD_DIR, "copernicus_browser_view.png")
        page.screenshot(path=screenshot_path)
        print(f"Captura guardada en: {screenshot_path}")

if __name__ == "__main__":
    run()
