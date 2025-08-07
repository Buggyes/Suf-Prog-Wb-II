from fastapi import Depends, FastAPI, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from sqlmodel import create_engine, Session
from http import HTTPStatus
from sqlmodel import select
from models import *
from services import *

# URL do banco, não mudar isso em circumstância nenhuma
database_url = "postgresql://localhost/rest_api_furb"

engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(root_path="/RestAPIFurb")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Chamadas da API

@app.post("/usuario")
def create_usuario(usuario: UsuarioDTO, session: SessionDep):
    expression = select(Usuario).where(Usuario.nome == usuario.nome).where(Usuario.telefone == usuario.telefone)
    result = session.exec(expression).first()
    
    if result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário já existe")
    
    #added_usuario = Usuario(nome=usuario.nome, telefone=usuario.telefone)
    added_usuario = Usuario.from_orm(usuario)
    session.add(added_usuario)
    session.commit()
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Usuário criado com sucesso"})
        

@app.get("/comandas")
def get_comandas(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    comandas = session.exec(
        select(ComandaDTO).offset(offset).limit(limit)
    ).all()

    result = []

    for comanda in comandas:
        result.append({
            "idUsuario": comanda.idUsuario,
            "nomeUsuario": comanda.nomeUsuario,
            "telefoneUsuario": comanda.telefoneUsuario,
        })
    
    return JSONResponse(content=result)

@app.get("/comandas/{id}")
def get_comanda_by_id(
    id: int,
    session: SessionDep,
):
    comanda = session.exec(
        select(Comanda).where(Comanda.id == id)
    ).first()

    produtosIds = session.exec(
        select(Comanda_Produto).where(Comanda_Produto.idComanda == id)
    ).all()
    
    produtos = session.exec(select(Produto).where(Produto.id.in_(produtosIds))).all()

    produtosFinais = []

    for produto in produtos:
        produtosFinais.append({
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco
        })

    result = {
        "idUsuario": comanda.idUsuario,
        "nomeUsuario": comanda.nomeUsuario,
        "telefoneUsuario": comanda.telefoneUsuario,
        "produtos": produtosFinais
    }

    
    return JSONResponse(content=result)

#TODO: Terminar esse método (fazer as relações na tabela comanda_produto na hora de adicionar a comanda)
@app.post("/comandas")
def post_comanda(
    session: SessionDep,
    comanda: ComandaPostDTO
):
    usuarioCheck = session.exec(select(Usuario).where(Usuario.id == comanda.idUsuario))

    if not usuarioCheck:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário passado por parâmetro não está cadastrado.")

    produtos = comanda.produtos
    for produto in produtos:
        dbProduto = Produto.from_orm(produto)
        session.add(dbProduto)
        session.commit()


@app.delete("/comandas/{id}")
def delete_comanda_by_id(
    id: int,
    session: SessionDep,
):
    comandaProdutos = session.exec(select(Comanda_Produto).where(Comanda_Produto.idComanda == id)).all()
    for comandaProduto in comandaProdutos:
        session.delete(comandaProduto)
    session.commit()
    
    comanda = session.exec(select(Comanda).where(Comanda.id == id)).first()
    session.delete(comanda)
    session.commit()

    return JSONResponse({"success":{"text":"comanda removida"}})