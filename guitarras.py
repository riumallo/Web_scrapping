from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Parametros de la automatizacion.
# PRODUCTO = "Audifonos"
AMAZON_URL = "https://www.musicman.es/instruments/guitars/the-majesty"


def build_driver() -> webdriver.Chrome | None:
    """Crea el driver de Chrome, usando chrome portable local si existe."""
    chrome_binary = Path(__file__).parent / "chrome-win64" / "chrome.exe"
    options = Options()
    if chrome_binary.exists():
        options.binary_location = str(chrome_binary)

    try:
        return webdriver.Chrome(options=options)
    except WebDriverException as exc:
        print("No se pudo iniciar Chrome WebDriver.")
        print("Verifica que Chrome/chromedriver sean compatibles.")
        print(f"Detalle: {exc}")
        return None
# funcion para abrir el link de la pagina
def abrir_pagina(driver: webdriver.Chrome, url: str) -> None:
    """Abre la pagina dada por url."""
    driver.get(url) 

    # buyscamos el boton con id = "jsMageButton" para haceer click
    wait = WebDriverWait(driver, 30)

    # antes de hacer click cerraremos el modal precionando este elemento <a class="close" data-dismiss="modal" aria-label="Close"> <div id="cross"> <div class="cross-outer"> <div class="cross-inner"></div> </div> </div></a>
    try:
        cerrar_modal = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.close[data-dismiss='modal']"))
        )
        cerrar_modal.click()
    except Exception as e:
        print("No se pudo cerrar el modal o no estaba presente.")
        print(f"Detalle: {e}")
        



    boton = wait.until(
        EC.element_to_be_clickable((By.ID, "jsMageButton"))
    )
    boton.click()





def main() -> None:
    driver = build_driver()
    if driver is None:
        return

    try:
        abrir_pagina(driver, AMAZON_URL)
        input("Presiona Enter para cerrar...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

