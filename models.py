from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from decimal import getcontext, Decimal

getcontext().prec = 2

class Comanda_Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    idComanda: int = Field(foreign_key="comanda.id")
    idProduto: int = Field(foreign_key="produto.id")

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    telefone: str

class Comanda(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    idUsuario: int = Field(foreign_key="usuario.id")
    produtos: List["Produto"] = Relationship(
        back_populates="comandas",
        link_model=Comanda_Produto
    )

class Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    preco: Decimal
    comandas: List["Comanda"] = Relationship(
        back_populates="produtos",
        link_model=Comanda_Produto
    )


#DTOs

class UsuarioDTO(BaseModel):
    id: Optional[int] = None
    nome: str
    telefone: str

class ProdutoDTO(BaseModel):
    id: Optional[int] = None
    nome: str
    preco: Decimal

class ComandaDTO(BaseModel):
    id: Optional[int] = None
    idUsuario: int
    nomeUsuario: str
    telefoneUsuario: str
    produtos: List[ProdutoDTO]

class ComandaPostDTO(BaseModel):
    idUsuario: int
    nomeUsuario: str
    telefoneUsuario: str
    produtos: List[ProdutoDTO]