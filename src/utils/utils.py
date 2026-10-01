import logging
import re
import subprocess
import win32con
import win32gui
import win32process

from datetime import datetime
from pathlib import Path
from PIL import ImageGrab
from selenium.webdriver.remote.webdriver import WebDriver

from src.context import CTX

logger = logging.getLogger("desafio_rpa")


def maximizar_janela_processo(processo: subprocess.Popen) -> bool:
    try:
        if processo.poll() is not None:
            logger.error("O processo %s já foi encerrado", processo.pid)
            return False

        janelas: list[tuple[int, int]] = []

        def verificar_janela(hwnd: int, _) -> None:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            if pid != processo.pid:
                return
            if not win32gui.IsWindowVisible(hwnd):
                return
            if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
                return
            if not win32gui.GetWindowText(hwnd).strip():
                return

            _, _, _, _, retangulo = win32gui.GetWindowPlacement(hwnd)
            esquerda, topo, direita, base = retangulo
            area = max(0, direita - esquerda) * max(0, base - topo)

            if area > 0:
                janelas.append((area, hwnd))

        win32gui.EnumWindows(verificar_janela, None)

        if not janelas:
            logger.error(
                "Nenhuma janela principal encontrada para o PID %s",
                processo.pid,
            )
            return False

        _, hwnd = max(janelas, key=lambda janela: janela[0])

        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        _, estado, _, _, _ = win32gui.GetWindowPlacement(hwnd)
        sucesso = estado == win32con.SW_SHOWMAXIMIZED
        if not sucesso:
            logger.error("Não foi possível maximizar a janela: PID %s", processo.pid)

        return sucesso

    except Exception:
        logger.exception("Falha ao maximizar a janela do processo")
        return False


def salvar_screenshot_processo(
    processo: subprocess.Popen,
    caminho: str | Path,
) -> Path:
    """Captura a janela principal do processo e salva como PNG."""
    if processo.poll() is not None:
        raise RuntimeError(
            f"O processo {processo.pid} já foi encerrado"
        )

    janelas: list[tuple[int, int]] = []

    def verificar_janela(hwnd: int, _) -> None:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        if pid != processo.pid:
            return

        if not win32gui.IsWindowVisible(hwnd):
            return

        if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
            return

        if not win32gui.GetWindowText(hwnd).strip():
            return

        esquerda, topo, direita, base = win32gui.GetWindowRect(hwnd)
        area = max(0, direita - esquerda) * max(0, base - topo)

        if area > 0:
            janelas.append((area, hwnd))

    win32gui.EnumWindows(verificar_janela, None)

    if not janelas:
        raise RuntimeError(
            f"Nenhuma janela principal encontrada para o PID {processo.pid}"
        )

    _, hwnd = max(janelas, key=lambda janela: janela[0])

    if win32gui.IsIconic(hwnd):
        raise RuntimeError(
            "A janela está minimizada; restaure-a antes da captura"
        )

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    imagem = ImageGrab.grab(window=hwnd)
    try:
        imagem.save(caminho, format="PNG")
    finally:
        imagem.close()

    return caminho


def salvar_screenshot_erro(
    nome: str = "erro", driver: WebDriver | None = None
) -> Path | None:
    """Salva um PNG em resultados/<execucao>/screenshots/.

    Com `driver`, captura a janela do navegador. Sem ele, captura a tela
    do desktop. Uma falha na captura é registrada e retorna None, sem
    substituir a exceção que motivou a chamada.
    """
    try:
        nome_seguro = re.sub(r"[^A-Za-z0-9_-]+", "_", nome).strip("_") or "erro"
        pasta = CTX.caminho_resultado("screenshots")
        pasta.mkdir(parents=True, exist_ok=True)
        instante = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        caminho = pasta / f"{nome_seguro}_{instante}.png"

        if driver is not None:
            if not driver.save_screenshot(str(caminho)):
                raise OSError("O Selenium não conseguiu salvar a captura")
        else:
            import pyautogui

            pyautogui.screenshot(str(caminho))

        logger.info("Screenshot de erro salvo: %s", caminho)
        return caminho
    except Exception:
        logger.exception("Não foi possível salvar o screenshot de erro")
        return None
