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
    idUsuario: int = Field(foreign_key="usuario.id")

class Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(default=None)
    preco: Decimal = Field(default=None)

class Comanda_Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    idComanda: int = Field(foreign_key="comanda.id")
    idProduto: int = Field(foreign_key="produto.id")

#DTOs

class UsuarioDTO(BaseModel):
    id: Optional[int] = None
    nome: str
    telefone: str

class ProdutoDTO(BaseModel):
    id: Optional[int] = None
    nome: str
    preco: Decimal

class Comanda(BaseModel):
    id: Optional[int] = None
    idUsuario: int
    nomeUsuario: str
    telefoneUsuario: str
    produtos: List[ProdutoDTO] = list()