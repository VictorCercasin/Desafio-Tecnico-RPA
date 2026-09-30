import time
import math
import pyautogui
from pathlib import Path
from typing import Any



from src.context import CTX


import pyautogui


def _validar_parametros(timeout: float, intervalo: float, confidence: float) -> None:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout deve ser finito e maior que 0")
    if not math.isfinite(intervalo) or intervalo <= 0:
        raise ValueError("intervalo deve ser finito e maior que 0")
    if not math.isfinite(confidence) or not 0 < confidence <= 1:
        raise ValueError("confidence deve estar entre 0 (exclusivo) e 1")


def _localizar_imagem(imagem: str, confidence: float) -> Any:
    try:
        return pyautogui.locateOnScreen(imagem, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return None


def _esperar_localizacao(
    imagem: str, timeout: float, intervalo: float, confidence: float
) -> Any:
    limite = time.monotonic() + timeout
    while True:
        localizacao = _localizar_imagem(imagem, confidence)
        if localizacao is not None:
            return localizacao
        restante = limite - time.monotonic()
        if restante <= 0:
            raise TimeoutError(
                f"Imagem não encontrada após {timeout} segundos: {imagem}"
            )
        time.sleep(min(intervalo, restante))


def esperar_imagem(
    imagem: str | Path,
    timeout: float = 10,
    intervalo: float = 0.5,
    confidence: float = 0.8,
) -> bool:
    """Aguarda a imagem; retorna True ou levanta TimeoutError."""
    _validar_parametros(timeout, intervalo, confidence)
    _esperar_localizacao(str(imagem), timeout, intervalo, confidence)
    return True


def clicar_imagem(
    imagem: str | Path,
    proxima_imagem: str | Path | None = None,
    timeout: float = 10,
    tentativas: int = 3,
    intervalo: float = 0.5,
    confidence: float = 0.8,
    *,
    repetir_clique: bool = False,
) -> bool:
    """Aguarda o alvo, clica e opcionalmente aguarda uma imagem de confirmação.

    Se proxima_imagem=None, retorna True imediatamente após o clique e não
    repete a ação, pois não há confirmação que permita determinar falha.

    Por padrão, executa no máximo um clique, mesmo com tentativas > 1.
    repetir_clique=True permite até tentativas cliques quando existe uma
    imagem de confirmação; habilite somente quando repetir a ação for seguro.

    timeout se aplica separadamente à localização do alvo e à confirmação,
    em cada tentativa. As buscas de imagem podem exceder esse tempo.

    Retorna True após o clique quando não há confirmação, ou quando a imagem
    de confirmação aparece. Levanta TimeoutError se o alvo ou a confirmação
    não aparecer. Outros erros são propagados, inclusive o mecanismo de
    emergência (FailSafe) do PyAutoGUI.
    """
    _validar_parametros(timeout, intervalo, confidence)

    if (
        isinstance(tentativas, bool)
        or not isinstance(tentativas, int)
        or tentativas < 1
    ):
        raise ValueError(
            "tentativas deve ser um inteiro maior ou igual a 1"
        )

    imagem = str(imagem)

    if proxima_imagem is not None:
        proxima_imagem = str(proxima_imagem)

    # Sem confirmação não temos base segura para repetir o clique.
    total = (
        tentativas
        if repetir_clique and proxima_imagem is not None
        else 1
    )

    for tentativa in range(1, total + 1):
        localizacao = _esperar_localizacao(
            imagem,
            timeout,
            intervalo,
            confidence,
        )

        pyautogui.click(pyautogui.center(localizacao))

        if proxima_imagem is None:
            return True

        try:
            return esperar_imagem(
                proxima_imagem,
                timeout,
                intervalo,
                confidence,
            )
        except TimeoutError as erro:
            if tentativa == total:
                raise TimeoutError(
                    f"Transição não confirmada após {tentativa} clique(s): "
                    f"{proxima_imagem}. A ação pode ter sido executada."
                ) from erro

def caminho_imagem(nome: str) -> str:
    caminho = CTX.assets_dir / f"{nome}.png"

    if not caminho.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {caminho}")

    return str(caminho)