import csv
import logging
from pathlib import Path

from src.context import CTX
from src.schemas import Comprador, Produto

logger = logging.getLogger("desafio_rpa")


def salvar_comprador_csv(comprador: Comprador) -> Path:
    """Grava o comprador da execução e devolve o caminho do CSV."""
    caminho = CTX.comprador_csv

    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["nome", "sobrenome", "cep", "status"])
        escritor.writeheader()
        escritor.writerow(
            {
                "nome": comprador.nome,
                "sobrenome": comprador.sobrenome,
                "cep": comprador.cep,
                "status": comprador.status,
            }
        )

    logger.info("CSV do comprador salvo: %s", caminho)
    return caminho


def salvar_catalogo_csv(produtos: list[Produto]) -> Path:
    """Grava todos os produtos da execução e devolve o caminho do CSV."""
    if not produtos:
        raise ValueError("Não é possível salvar um catálogo vazio")

    caminho = CTX.catalogo_csv

    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=["numero", "nome", "descricao", "preco", "status"]
        )
        escritor.writeheader()
        for produto in produtos:
            escritor.writerow(
                {
                    "numero": produto.numero,
                    "nome": produto.nome,
                    "descricao": produto.descricao,
                    "preco": format(produto.preco, ".2f"),
                    "status": produto.status
                }
            )

    logger.info("CSV do catálogo salvo: %s (%s produtos)", caminho, len(produtos))
    return caminho



def marcar_comprador_cadastrado() -> None:
    """Atualiza o status do único comprador no CSV da execução."""
    caminho = CTX.comprador_csv

    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames
        compradores = list(leitor)

    if len(compradores) != 1:
        raise ValueError("O CSV deve conter exatamente um comprador")

    if not colunas or "status" not in colunas:
        raise ValueError("O CSV do comprador não contém a coluna status")

    comprador = compradores[0]

    if comprador["status"] == "cadastrado":
        return

    if comprador["status"] != "coletado":
        raise ValueError(
            f"Status do comprador inválido: {comprador['status']!r}"
        )

    comprador["status"] = "cadastrado"
    temporario = caminho.with_suffix(".tmp")

    try:
        with temporario.open(
            "w", newline="", encoding="utf-8-sig"
        ) as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=colunas)
            escritor.writeheader()
            escritor.writerow(comprador)

        temporario.replace(caminho)
    finally:
        temporario.unlink(missing_ok=True)

    logger.info("Status do comprador atualizado para cadastrado")



def marcar_produto_cadastrado(numero: int) -> None:
    """Atualiza o status de um produto, preservando os demais registros."""
    caminho = CTX.catalogo_csv

    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames
        produtos = list(leitor)

    if not colunas or not {"numero", "status"}.issubset(colunas):
        raise ValueError("O catálogo deve conter as colunas numero e status")

    correspondencias = [
        produto
        for produto in produtos
        if int(produto["numero"]) == numero
    ]

    if len(correspondencias) != 1:
        raise ValueError(
            f"Esperado exatamente um produto com número {numero}; "
            f"encontrados {len(correspondencias)}"
        )

    produto = correspondencias[0]

    if produto["status"] == "cadastrado":
        return

    if produto["status"] != "coletado":
        raise ValueError(
            f"Status inválido para o produto {numero}: {produto['status']!r}"
        )

    produto["status"] = "cadastrado"
    temporario = caminho.with_suffix(".tmp")

    try:
        with temporario.open(
            "w", newline="", encoding="utf-8-sig"
        ) as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=colunas)
            escritor.writeheader()
            escritor.writerows(produtos)

        temporario.replace(caminho)
    finally:
        temporario.unlink(missing_ok=True)

    logger.info("Produto %s marcado como cadastrado no CSV", numero)

