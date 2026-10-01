import argparse
import logging
from pathlib import Path

from src.settings import PATH
from src.config_logger import configurar_logger
from src.context import CTX
from src.csv import salvar_comprador_csv, salvar_catalogo_csv
from src.fakenamegenerator import coletar_comprador_fake
from src.saucedemo import coletar_catalogo
from src.fakturama import cadastrar_dados_fakturama


logger = logging.getLogger("desafio_rpa")


def main() -> bool:

    args = parse_args()
    path_fakturama_exe = args.fakturama_exe.resolve()

    CTX.init_defaults(base_dir=Path(__file__).resolve().parent, path_fakturama_exe = path_fakturama_exe)
    configurar_logger(CTX.resultados_dir)

    logger.info("Executável do Fakturama: %s", path_fakturama_exe)


    logger.info("Iniciando coleta de dados do comprador fake")
    try:
        comprador = coletar_comprador_fake()
        salvar_comprador_csv(comprador=comprador)
    except Exception:
        logger.exception("Houve uma falha na coleta de um comprador fake.")
        return False


    logger.info("Iniciando coleta de dados do catálogo")
    try:
        catalogo = coletar_catalogo()
        salvar_catalogo_csv(catalogo)
    except Exception:
        logger.exception("Houve uma falha na coleta do catálogo.")
        return False

    logger.info("Iniciando cadastro dos dados no Fakturama")
    try:
        cadastrar_dados_fakturama()
    except Exception:
        logger.exception("Houve uma falha ao cadastrar dados no fakturama.")
        return False



    return True



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Coleta dados na web e os cadastra no Fakturama."
    )
    parser.add_argument(
        "-p",
        "--fakturama-exe",
        type=Path,
        default=PATH["fakturama"],
        metavar="CAMINHO",
        help="Caminho para o executável do Fakturama.",
    )

    args = parser.parse_args()
    if not args.fakturama_exe.is_file():
        parser.error(f"Executável do Fakturama não encontrado: {args.fakturama_exe}")
    return args





if __name__ == "__main__":
    resultado = main()
    if resultado:
        logger.info("Execução finalizada com sucesso")
    else:
        logger.critical("Houve uma falha catastrófica. Finalizando execução")

    raise SystemExit(0 if resultado else 1)
