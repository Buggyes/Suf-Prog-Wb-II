from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Field, SQLModel, Column
from decimal import getcontext, Decimal

getcontext().prec = 2

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(default=None)
    telefone: str = Field(default=True)

class Comanda(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")

class Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(default=None)
    preco: Decimal = Field(default=None)

class Comanda_Produto():
    id: int | None = Field(default=None, primary_key=True)
    id_comanda: int = Field(foreign_key="comanda.id")
    id_produto: int = Field(foreign_key="produto.id")

#DTOs

class UsuarioDTO(BaseModel):
    nome: str

class ProdutoDTO(BaseModel):
    id: int
    nome: str
    preco: Decimal

class Comanda(BaseModel):
    idUsuario: int
    nomeUsuario: str
    telefoneUsuario: str
    produtos: List[ProdutoDTO] = list()