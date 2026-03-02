from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


def main() -> None:
    chrome_binary = Path(__file__).parent / "chrome-win64" / "chrome.exe"

    options = Options()
    if chrome_binary.exists():
        options.binary_location = str(chrome_binary)

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as exc:
        print("No se pudo iniciar Chrome WebDriver.")
        print("Verifica que Chrome/chromedriver sean compatibles.")
        print(f"Detalle: {exc}")
        return

    try:
        driver.get("https://www.google.com")
        input("Presiona Enter para cerrar...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
