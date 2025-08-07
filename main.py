from fastapi import Depends, FastAPI, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from sqlmodel import create_engine, Session
from http import HTTPStatus
from sqlmodel import select
from models import *

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


@app.post("/usuario")
def create_usuario(usuario: UsuarioDTO, session: SessionDep):
    result = session.exec(select(Usuario)
    .where(Usuario.nome == usuario.nome)
    ).first()
    
    if result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário já existe")
    
    addedUsuario = Usuario.from_orm(usuario)
    session.add(addedUsuario)
    session.commit()
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Usuário criado com sucesso"})
        

@app.get("/comandas")
def get_comandas(
    session: SessionDep,
    limit: Annotated[int, Query(le=100)] = 100,
):
    comandas = session.exec(
        select(Comanda).limit(limit)
    ).all()

    usuarios = []
    for comanda in comandas:
        usuarios.append(session.exec(select(Usuario)
            .where(Usuario.id == comanda.id_usuario)
            ).first())
    result = []

    for usuario in usuarios:
        result.append({
            "idUsuario": usuario.id,
            "nomeUsuario": usuario.nome,
            "telefoneUsuario": usuario.telefone,
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
    if not comanda:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="Comanda não encontrada")

    produtosIds = session.exec(
        select(Comanda_Produto.id_produto)
        .where(Comanda_Produto.id_comanda == id)
    ).all()
    
    produtos = session.exec(
        select(Produto)
        .where(Produto.id.in_(produtosIds))
        ).all()

    produtosFinais = []

    for produto in produtos:
        produtosFinais.append({
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco
        })

    usuario = session.exec(
        select(Usuario)
        .where(Usuario.id == comanda.id_usuario)
    ).first()

    result = {
        "idUsuario": usuario.id,
        "nomeUsuario": usuario.nome,
        "telefoneUsuario": usuario.telefone,
        "produtos": produtosFinais
    }
    
    return JSONResponse(content=result)

@app.post("/comandas")
def post_comanda(
    session: SessionDep,
    comanda: ComandaPostDTO
):
    usuarioCheck = session.exec(
        select(Usuario).where(Usuario.id == comanda.id_usuario
        or Usuario.nome == comanda.nome_usuario
        or Usuario.telefone == comanda.telefone_usuario)
        ).first()

    if not usuarioCheck:
        addedUsuario = Usuario(
            id=comanda.id_usuario,
            nome=comanda.nome_usuario,
            telefone=comanda.telefone_usuario
        )
        session.add(addedUsuario)
        session.commit()
        session.refresh(addedUsuario)

    produtos = comanda.produtos
    for produto in produtos:
        produtoCheck = session.exec(
            select(Produto).where(Produto.id == produto.id)
            ).first()
        if not produtoCheck:
            produto.preco = round(produto.preco, 2)
            dbProduto = Produto.from_orm(produto)
            session.add(dbProduto)
    session.commit()
    
    dbProdutos = []
    for produto in produtos:
        dbProdutos.append(session.exec(select(Produto)
        .where(Produto.id == produto.id)).first())
    
    addedComanda = Comanda(id_usuario=comanda.id_usuario)
    session.add(addedComanda)
    session.commit()
    session.refresh(addedComanda)

    for dbProduto in dbProdutos:
        addedComandaProduto = Comanda_Produto(id_comanda=addedComanda.id, id_produto=dbProduto.id)
        session.add(addedComandaProduto)
        session.commit()
    return get_comanda_by_id(addedComanda.id, session)

@app.put("/comandas/{id}")
def put_comanda_by_id(
    id: int,
    produtos: List[ProdutoPutDTO],
    session: SessionDep
):
    comanda = session.exec(select(Comanda)
    .where(Comanda.id == id)
    ).first()
    
    if not comanda:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="Comanda não encontrada")

    produtoIds = [p.id for p in produtos]
    dbProdutos = session.exec(
        select(Produto).where(Produto.id.in_(produtoIds))
        ).all()
    produtoIds = {p.id for p in dbProdutos}
    for produto in produtos:
        if produto.id not in produtoIds:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="A comanda não possui um produto com o id: "+produto.id.__str__())
        dbProduto.nome = produto.nome
        dbProduto.preco = round(produto.preco,2)
        session.add(dbProduto)
    session.commit()
    
    return get_comanda_by_id(id, session)

@app.delete("/comandas/{id}")
def delete_comanda_by_id(
    id: int,
    session: SessionDep,
):
    comanda = session.exec(select(Comanda).where(Comanda.id == id)).first()
    if not comanda:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="Comanda não encontrada")

    comandaProdutos = session.exec(select(Comanda_Produto).where(Comanda_Produto.id_comanda == id)).all()
    produtosIds = []
    for comandaProduto in comandaProdutos:
        produtosIds.append(comandaProduto.id_produto)
        session.delete(comandaProduto)
    session.commit()

    session.delete(comanda)
    session.commit()

    return JSONResponse({"success":{"text":"comanda removida"}})