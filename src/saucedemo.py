import logging
import re
from decimal import Decimal

from bs4 import BeautifulSoup

from selenium.common.exceptions import (
    WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from src.schemas import Produto
from src.utils.driver import config_driver, clicar_elemento
from src.settings import URL
from src.utils.utils import salvar_screenshot_erro



logger = logging.getLogger("desafio_rpa")


def coletar_catalogo(tentativas: int = 3)-> list[Produto]:
    if tentativas <= 0:
        raise ValueError("tentativas deve ser maior que 0")
    for tentativa in range(1, tentativas + 1):
        driver = None
        try:
            logger.info("Coleta web: tentativa %s de %s", tentativa, tentativas)
            driver = config_driver(headless=False)
            produtos = coletar_catalogo_executar(driver)
            

            return produtos

        except WebDriverException:
            logger.exception("Falha transitória na coleta web")
            salvar_screenshot_erro(nome="coleta_catalogo", driver=driver)
            if tentativa == tentativas:
                raise

        except Exception:
            logger.exception("Houve uma falha inesperada na coleta do catálogo")
            salvar_screenshot_erro(nome="coleta_catalogo")
            raise

        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    logger.warning("Falha ao fechar o driver")


def coletar_catalogo_executar(driver: WebDriver) -> list[Produto]:
    login_saucedemo(driver=driver)
    produtos = extrair_catalogo_html(driver)


    return produtos



def extrair_catalogo_html(driver: WebDriver) -> list[Produto]:
    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "inventory_item")
            )
        )
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    elementos_produto = soup.select(".inventory_item")

    if not elementos_produto:
        raise ValueError("Nenhum produto encontrado no catálogo")

    produtos = []

    for elemento in elementos_produto:
        elemento_nome = elemento.select_one(".inventory_item_name")
        elemento_descricao = elemento.select_one(".inventory_item_desc")
        elemento_preco = elemento.select_one(".inventory_item_price")
        elemento_link = elemento.select_one("[id^='item_'][id$='_title_link']")

        if elemento_nome is None:
            raise ValueError("Nome de produto não encontrado")

        if elemento_descricao is None:
            raise ValueError("Descrição de produto não encontrada")

        if elemento_preco is None:
            raise ValueError("Preço de produto não encontrado")

        if elemento_link is None:
            raise ValueError("Número do produto não encontrado")

        match_numero = re.search(
            r"item_(\d+)_title_link",
            elemento_link.get("id", ""),
        )

        if match_numero is None:
            raise ValueError("Número do produto inválido")

        numero = int(match_numero.group(1))

        preco = Decimal(
            elemento_preco
            .get_text(strip=True)
            .replace("$", "")
        )

        produtos.append(
            Produto(
                numero=numero,
                nome=elemento_nome.get_text(strip=True),
                descricao=elemento_descricao.get_text(strip=True),
                preco=preco,
                status="coletado"
            )
        )
        logger.info(f"Produto extraído: {produtos[-1]}")

    return produtos

def login_saucedemo(driver: WebDriver):
    driver.get(URL["saucedemo"])
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID, "login_credentials")
        )
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")

    elemento_usuarios = soup.select_one("#login_credentials")
    if elemento_usuarios is None:
        raise ValueError("Credenciais de usuário não encontradas na página")

    usuarios = [
        texto.strip()
        for texto in elemento_usuarios.stripped_strings
        if texto.strip() != "Accepted usernames are:"
    ]

    if not usuarios:
        raise ValueError("Nenhum usuário disponível encontrado")

    elemento_senha = soup.select_one(".login_password")
    if elemento_senha is None:
        raise ValueError("Senha não encontrada na página")

    textos_senha = [
        texto.strip()
        for texto in elemento_senha.stripped_strings
        if texto.strip() != "Password for all users:"
    ]

    if not textos_senha:
        raise ValueError("Senha disponível não encontrada")

    usuario = usuarios[0]
    senha = textos_senha[0]

    campo_usuario = driver.find_element(By.ID, "user-name")
    campo_senha = driver.find_element(By.ID, "password")
    botao_login = driver.find_element(By.ID, "login-button")

    campo_usuario.send_keys(usuario)
    campo_senha.send_keys(senha)
    botao_login.click()