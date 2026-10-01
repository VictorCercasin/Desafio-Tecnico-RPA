import logging
from pathlib import Path
from colorlog import ColoredFormatter

LOGGER_NAME = "desafio_rpa"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s | %(filename)s:%(lineno)d"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configurar_logger(resultados_dir: Path) -> logging.Logger:
    """Grava exec.log na pasta da execução e mostra INFO ou superior no console."""
    resultados_dir = Path(resultados_dir)
    resultados_dir.mkdir(parents=True, exist_ok=True)
    arquivo_log = resultados_dir / "exec.log"

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Permite configurar outra execução no mesmo processo sem duplicar mensagens.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        ColoredFormatter(
            "%(log_color)s" + LOG_FORMAT + "%(reset)s",
            datefmt=DATE_FORMAT,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    arquivo = logging.FileHandler(arquivo_log, mode="w", encoding="utf-8")
    arquivo.setLevel(logging.DEBUG)
    arquivo.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    logger.addHandler(console)
    logger.addHandler(arquivo)
    logger.info("Log iniciado: %s", arquivo_log)
    return logger
