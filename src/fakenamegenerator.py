import logging
import re
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.driver import config_driver, clicar_elemento
from src.settings import URL
from src.schemas import Comprador
from src.utils.utils import salvar_screenshot_erro



logger = logging.getLogger("desafio_rpa")

def coletar_comprador_fake(tentativas: int = 3) -> Comprador:
    if tentativas <= 0:
        raise ValueError("tentativas deve ser maior que 0")
    for tentativa in range(1, tentativas + 1):
        driver = None
        try:
            logger.info("Coleta web: tentativa %s de %s", tentativa, tentativas)
            driver = config_driver(headless=False)
            comprador = coletar_comprador_fake_executar(driver)
            logger.info(f"Comprador extraído: {comprador}")

            return comprador

        except WebDriverException:
            logger.exception("Falha transitória na coleta web")
            salvar_screenshot_erro(nome="coleta_comprador_fake", driver=driver)
            if tentativa == tentativas:
                raise

        except Exception:
            logger.exception("Houve uma falha inesperada na coleta do comprador fake")
            salvar_screenshot_erro(nome="coleta_comprador_fake")
            raise

        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    logger.warning("Falha ao fechar o driver")


def coletar_comprador_fake_executar(driver: WebDriver) -> Comprador:
    driver.get(URL["fakenamegenerator"])
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.address h3")
        )
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")

    elemento_nome = soup.select_one("div.address h3")
    if elemento_nome is None:
        raise ValueError("Nome do comprador não encontrado na página")

    partes_nome = elemento_nome.get_text(strip=True).split(maxsplit=1)
    if len(partes_nome) < 2:
        raise ValueError("Nome completo do comprador não contém sobrenome")

    elemento_endereco = soup.select_one("div.address div.adr")
    if elemento_endereco is None:
        raise ValueError("Endereço do comprador não encontrado na página")

    endereco = elemento_endereco.get_text(" ", strip=True)
    match_cep = re.search(r"\b\d{5}-\d{3}\b", endereco)
    if match_cep is None:
        raise ValueError("CEP não encontrado no endereço do comprador")

    return Comprador(
        nome=partes_nome[0],
        sobrenome=partes_nome[1],
        cep=match_cep.group(),
        status="coletado",
    )
    



