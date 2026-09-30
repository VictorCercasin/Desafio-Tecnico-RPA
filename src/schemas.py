# src/schemas.py
from pydantic import BaseModel, Field
from typing import Literal
from decimal import Decimal


class Comprador(BaseModel):
    nome: str = Field(min_length=1)
    sobrenome: str = Field(min_length=1)
    cep: str = Field(pattern=r"^\d{5}-?\d{3}$")
    status: Literal["coletado", "cadastrado"]
    



class Produto(BaseModel):
    numero: int = Field(ge=0)
    nome: str = Field(min_length=1)
    preco: Decimal = Field(gt=0)
    descricao: str = Field(min_length=1)
    status: Literal["coletado", "cadastrado"]