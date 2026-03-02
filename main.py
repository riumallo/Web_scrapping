from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configuracion del login (declarada en codigo para pruebas/demos).
USER = "PRUEBA-GDE"
PASSWORD = "PRUEBA-GDE"
LOGIN_URL = "https://gestion.rld.cl/"


def build_driver() -> webdriver.Chrome | None:
    # Usa Chrome portable local si existe.
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


def login(driver: webdriver.Chrome, user: str, password: str) -> None:
    # Abre la pagina y espera a que los campos esten listos antes de interactuar.
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 20)

    email_input = wait.until(EC.visibility_of_element_located((By.NAME, "Email")))
    password_input = wait.until(EC.visibility_of_element_located((By.NAME, "Password")))
    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )

    # Completa formulario y envia.
    email_input.clear()
    email_input.send_keys(user)
    password_input.clear()
    password_input.send_keys(password)
    submit_button.click()


def get_value_by_label(card, label_text: str) -> str:
    # Dentro de una tarjeta, busca el bloque "field" cuyo <label> coincide con label_text.
    # Luego toma el texto de <span class="value">, que es el dato numérico visible.
    value_element = card.find_element(
        By.XPATH,
        (
            ".//div[contains(@class,'field')]"
            f"[.//label[normalize-space()='{label_text}']]"
            "//span[contains(@class,'value')]"
        ),
    )
    return value_element.text.strip()


def extract_dashboard_metrics(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, 30)

    # Espera a estar realmente en dashboard.php para evitar leer datos antes de cargar.
    wait.until(EC.url_contains("dashboard.php"))

    # Espera el contenedor principal de métricas; desde aquí se leen las 3 tarjetas.
    metrics_wrap = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.metrics-wrap"))
    )

    # Tarjeta 1: DOCUMENTOS PERSONAL.
    personal_card = metrics_wrap.find_element(By.CSS_SELECTOR, ".form-card--personal")
    personal_total = get_value_by_label(personal_card, "Total documentos")
    personal_por_vencer = get_value_by_label(personal_card, "Por vencer")
    personal_vencidos = get_value_by_label(personal_card, "Vencidos")

    # Tarjeta 2: DOCUMENTOS RRHH (IDs directos cuando existen => más estable).
    rrhh_total = metrics_wrap.find_element(By.ID, "total_documentosRRHH").text.strip()
    rrhh_sin_firma = metrics_wrap.find_element(By.ID, "total_rrhh_sin_firma").text.strip()

    # Tarjeta 3: DOCUMENTOS PREVENCION (también usando IDs directos).
    prev_total = metrics_wrap.find_element(By.ID, "total_documentosCC").text.strip()
    prev_sin_firma = metrics_wrap.find_element(By.ID, "total_documentosPvCC").text.strip()

    print("\n=== METRICAS DASHBOARD ===")
    print(f"Documentos Personal -> Total: {personal_total}")
    print(
        "Documentos Personal -> "
        f"Por vencer: {personal_por_vencer} | Vencidos: {personal_vencidos}"
    )
    print(f"Documentos RRHH -> Total: {rrhh_total} | Sin firmar: {rrhh_sin_firma}")
    print(f"Documentos Prevencion -> Total: {prev_total} | Sin firmar: {prev_sin_firma}")
    print("==========================\n")


def main() -> None:
    driver = build_driver()
    if driver is None:
        return

    try:
        login(driver, USER, PASSWORD)
        extract_dashboard_metrics(driver)
        input("Presiona Enter para cerrar...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
