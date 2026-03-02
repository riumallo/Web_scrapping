from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Parametros de la automatizacion.
PRODUCTO = "Audifonos"
AMAZON_URL = "https://www.amazon.com/"


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


def buscar_producto(driver: webdriver.Chrome, texto_busqueda: str) -> None:
    """Abre Amazon, escribe en el buscador y ejecuta la busqueda."""
    driver.get(AMAZON_URL)
    wait = WebDriverWait(driver, 20)

    search_input = wait.until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )
    submit_button = wait.until(
        EC.element_to_be_clickable((By.ID, "nav-search-submit-button"))
    )

    search_input.clear()
    search_input.send_keys(texto_busqueda)
    submit_button.click()


def extraer_productos(driver: webdriver.Chrome, limite: int = 10) -> None:
    """
    Extrae nombre y precio de resultados y los imprime.

    Como se extraen los datos:
    1) Primero esperamos contenedores de resultados: div[data-component-type='s-search-result'].
    2) Dentro de cada contenedor buscamos el nombre en 'h2 span'.
    3) El precio suele venir separado en dos partes:
       - entero: '.a-price-whole'
       - decimales: '.a-price-fraction'
    4) Si no hay precio visible, mostramos 'Sin precio visible'.
    """
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        )
    )

    resultados = driver.find_elements(
        By.CSS_SELECTOR, "div[data-component-type='s-search-result']"
    )

    print("\n=== PRODUCTOS ENCONTRADOS ===")
    impresos = 0

    for item in resultados:
        if impresos >= limite:
            break

        # Nombre del producto (etiqueta h2 > span dentro del resultado).
        titulo_elements = item.find_elements(By.CSS_SELECTOR, "h2 span")
        if not titulo_elements:
            continue
        nombre = titulo_elements[0].text.strip()
        if not nombre:
            continue

        # Precio: se arma con la parte entera y decimal.
        parte_entera = item.find_elements(By.CSS_SELECTOR, "span.a-price-whole")
        parte_decimal = item.find_elements(By.CSS_SELECTOR, "span.a-price-fraction")

        if parte_entera:
            entero = parte_entera[0].text.replace(",", "").strip()
            decimal = parte_decimal[0].text.strip() if parte_decimal else "00"
            precio = f"${entero}.{decimal}"
        else:
            precio = "Sin precio visible"

        impresos += 1
        print(f"{impresos}. {nombre} | Precio: {precio}")

    if impresos == 0:
        print("No se pudieron extraer productos con nombre/precio.")
    print("=============================\n")


def main() -> None:
    driver = build_driver()
    if driver is None:
        return

    try:
        buscar_producto(driver, PRODUCTO)
        extraer_productos(driver, limite=10)
        input("Presiona Enter para cerrar...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
