import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


logger = logging.getLogger("desafio_rpa")






def clicar_elemento(
    driver: WebDriver,
    xpath: str,
    next_xpath: str | None = None,
    timeout: float = 10,
    retries: int = 2,
) -> None:
    """Clica uma vez e, se solicitado, aguarda o próximo elemento visível.

    Repete apenas falhas ocorridas antes de um clique confirmado. Se a
    verificação posterior falhar, levanta TimeoutException sem clicar de novo.
    """
    if retries < 1:
        raise ValueError("retries deve ser pelo menos 1")

    for tentativa in range(retries):
        try:
            elemento = WebDriverWait(
                driver,
                timeout,
                poll_frequency=0.2,
                ignored_exceptions=(StaleElementReferenceException,),
            ).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            if tentativa == retries - 1:
                raise
            continue

        try:
            elemento.click()
        except (StaleElementReferenceException, ElementClickInterceptedException):
            if tentativa == retries - 1:
                raise
            continue

        # O clique retornou com sucesso: não o repetir por falha na verificação.
        break

    if next_xpath is not None:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, next_xpath))
        )


def config_driver(headless: bool = False) -> webdriver.Chrome:
    """Inicia Chrome; o Selenium Manager resolve o ChromeDriver."""
    prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.password_manager_leak_detection": False,
            }
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    options.add_experimental_option("prefs", prefs)

    

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    logger.info(
        "Chrome iniciado (%s; versão %s)",
        "headless" if headless else "visível",
        driver.capabilities.get("browserVersion", "desconhecida"),
    )
    return driver