import subprocess
import logging
import re
import csv
import pyperclip
import pyautogui
from decimal import Decimal
from pathlib import Path


from src.utils.utils import (salvar_screenshot_erro, salvar_screenshot_processo
                             , maximizar_janela_processo)
from src.context import CTX
from src.utils.imagens import (caminho_imagem, esperar_imagem, clicar_imagem)
from src.csv import marcar_comprador_cadastrado, marcar_produto_cadastrado
from src.schemas import Produto



logger = logging.getLogger("desafio_rpa")


def cadastrar_dados_fakturama(tentativas: int=3) -> bool:
    if tentativas <= 0:
        raise ValueError("tentativas deve ser maior que 0")
    for tentativa in range(1, tentativas + 1):
        fakturama_process = None
        try:
            path_fakturama_exe = CTX.path_fakturama_exe
            fakturama_process = abrir_fakturama_executar(path_fakturama_exe)
            esperar_imagem(caminho_imagem("prova_de_vida_fakturama"), timeout=300)
            # Aqui serão chamadas as funções para inserir o comprador e os produtos, portanto, o fakturama será fechado somente após o termino da execução
            cadastrar_comprador(fakturama_process)
            cadastrar_produtos(fakturama_process)
            return True

        except pyautogui.FailSafeException:
            logger.warning("Execução interrompida pelo FailSafe")
            raise

        except Exception:
            logger.exception("Falha ao cadastrar dados no fakturama")
            salvar_screenshot_erro(nome="cadastrar_dados_fakturama")
            if tentativa == tentativas:
                raise

        finally:
            if fakturama_process is not None:
                logger.info("Fechando Fakturama: %s", fakturama_process.pid)
                try:
                    fakturama_process.terminate()
                    fakturama_process.wait(timeout=10)
                except Exception:
                    logger.info("Não foi possível fechar Fakturama")


def cadastrar_produtos(fakturama_process: subprocess.Popen) -> bool:
    with CTX.catalogo_csv.open(
        "r", newline="", encoding="utf-8-sig"
    ) as arquivo:
        linhas = list(csv.DictReader(arquivo))

    if not linhas:
        raise ValueError("O CSV do catálogo está vazio")

    produtos = [Produto(**linha) for linha in linhas]

    numeros = [produto.numero for produto in produtos]
    if len(numeros) != len(set(numeros)):
        raise ValueError("O catálogo contém números de produto duplicados")

    if not maximizar_janela_processo(fakturama_process):
        logger.warning("Não foi possível maximizar o fakturama")

    def preencher_campo(texto: str) -> None:
        pyautogui.hotkey("ctrl", "a")
        pyperclip.copy(texto)
        pyautogui.hotkey("ctrl", "v")


    for produto in produtos:
        if produto.status == "cadastrado":
            logger.info(
                "Produto %s — %s já cadastrado; pulando",
                produto.numero,
                produto.nome,
            )
            continue

        logger.info(
            "Cadastrando produto %s — %s; preço: %s",
            produto.numero,
            produto.nome,
            format(produto.preco, ".2f"),
        )

        clicar_imagem(
            caminho_imagem("new_product"),
            caminho_imagem("item_number"),
            repetir_clique=True
        )
        clicar_imagem(caminho_imagem("item_number"))

        preencher_campo(str(produto.numero))

        # Item Number → Name
        pyautogui.press("tab")
        preencher_campo(produto.nome)

        # Name → Description
        pyautogui.press("tab", presses=4, interval=0.1)
        preencher_campo(produto.descricao)

        # Description → Price (gross)
        pyautogui.press("tab")
        preco_texto = format(produto.preco, ".2f").replace(".", ",")
        preencher_campo(preco_texto)
        logger.info("Preço: %s", format(produto.preco, ".2f"))

        # Sai do campo para processar o preço.
        pyautogui.press("tab")

        clicar_imagem(caminho_imagem("save"))
        marcar_produto_cadastrado(produto.numero)

        logger.info(
            "Fluxo de cadastro concluído para o produto %s — %s",
            produto.numero,
            produto.nome,
        )

    clicar_imagem(
        caminho_imagem("products"),
        caminho_imagem("products_active"),
    )

    salvar_screenshot_processo(fakturama_process, CTX.print_catalogo)
    logger.info("Screenshot do catálogo salvo: %s", CTX.print_catalogo)

    return True


def cadastrar_comprador(fakturama_process: subprocess.Popen) -> bool | None:
    with CTX.comprador_csv.open(
        "r", newline="", encoding="utf-8-sig"
    ) as arquivo:
        compradores = list(csv.DictReader(arquivo))

    if len(compradores) != 1:
        raise ValueError("O CSV deve conter exatamente um comprador")

    comprador = compradores[0]
    status = comprador.get("status")

    if status == "cadastrado":
        logger.info("Comprador já cadastrado; pulando cadastro")
        return True

    if status != "coletado":
        raise ValueError(f"Status do comprador inválido: {status!r}")

    maximizar_janela_processo(fakturama_process)

    logger.info(
        "Iniciando cadastro do comprador: %s %s",
        comprador["nome"],
        comprador["sobrenome"],
    )

    clicar_imagem(
        caminho_imagem("new_contact"),
        caminho_imagem("first_name"),
        repetir_clique=True
    )

    clicar_imagem(caminho_imagem("first_name"))

    pyautogui.hotkey("ctrl", "a")
    pyperclip.copy(comprador["nome"])
    pyautogui.hotkey("ctrl", "v")

    pyautogui.press("tab")
    pyautogui.hotkey("ctrl", "a")
    pyperclip.copy(comprador["sobrenome"])
    pyautogui.hotkey("ctrl", "v")

    pyautogui.press("tab", presses=8, interval=0.1)
    pyautogui.hotkey("ctrl", "a")
    pyperclip.copy(comprador["cep"])
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("tab")

    clicar_imagem(caminho_imagem("save"), caminho_imagem("debtors"))
    marcar_comprador_cadastrado()
    clicar_imagem(caminho_imagem("debtors"), caminho_imagem("debtors_active"))

    salvar_screenshot_processo(fakturama_process, CTX.print_comprador)
    logger.info("Save clicado para o comprador")
    logger.info("Status mudado com sucesso no CSV")
    return True



def abrir_fakturama_executar(caminho: str | Path) -> subprocess.Popen:
    executavel = Path(caminho).expanduser().resolve(strict=True)

    if not executavel.is_file():
        raise ValueError(f"O caminho não é um arquivo: {executavel}")

    processo = subprocess.Popen(
        [str(executavel)],
        cwd=str(executavel.parent),
    )

    logger.info("Fakturama iniciado. PID: %s", processo.pid)

    return processo