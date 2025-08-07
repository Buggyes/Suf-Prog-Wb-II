from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class Comanda_Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_comanda: int = Field(foreign_key="comanda.id")
    id_produto: int = Field(foreign_key="produto.id")

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    telefone: str

class Comanda(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    produtos: List["Produto"] = Relationship(
        back_populates="comandas",
        link_model=Comanda_Produto
    )

class Produto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    preco: float
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
    preco: float

class ComandaDTO(BaseModel):
    id: Optional[int] = None
    id_usuario: int
    nome_usuario: str
    telefone_usuario: str
    produtos: List[ProdutoDTO]

class ComandaPostDTO(BaseModel):
    id_usuario: int
    nome_usuario: str
    telefone_usuario: str
    produtos: List[ProdutoDTO]

class ProdutoPutDTO(BaseModel):
    id: int
    nome: str
    preco: float