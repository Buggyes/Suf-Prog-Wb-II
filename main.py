import traceback
from fastapi import Depends, FastAPI, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from sqlmodel import create_engine, Session
from http import HTTPStatus
from sqlmodel import select
from models import *
from usuario_service import *
from comanda_service import *

database_url = "postgresql://localhost/rest_api_furb"

engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(root_path="/RestAPIFurb",
            title="RestAPIFurb",
            description="Projeto implementado para a prova de suficiência de Programação Web II. Simula o fluxo de pedidos de uma lanchonete/restaurante.",
            )

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
def post_usuario(usuario: UsuarioDTO, session: SessionDep):
    """
    Cria um usuário sem nenhum vínculo a qualquer pedido.
    - **id**: Identificador do usuário. Caso encontre outro usuário com o mesmo id, mas nome e telefone diferentes, o banco define um id disponível automaticamente.
    - **nome**: Nome do usuário. Não é permitido ter 2 ou mais usuários com o mesmo nome.
    - **telefone**: Telefone do usuário. Mesma regra do nome.
    """
    try:
        result = cadastrar_usuario(usuario, session)
    except Exception as e:
        msg = e.args.__str__()
        if 'Usuário já existe' in msg:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=msg.__str__())
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Usuário criado com sucesso"})
        

@app.get("/comandas")
def get_comandas(
    session: SessionDep,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """
    Busca todas as comandas, apenas retornando quais usuários elas estão atreladas.
    - **limit**: Define o máximo de comandas que serão buscadas no banco (Padrão = 100).
    """
    return JSONResponse(content=buscar_comandas(limit, session))

@app.get("/comandas/{id}")
def get_comanda_by_id(
    id: int,
    session: SessionDep,
):
    """
    Busca uma comanda por id, retornando o usuário que fez o pedido, e todos os produtos no pedido.
    - **id**: Identificador da comanda.
    """
    try:
        result = buscar_comanda_by_id(id, session)
        return JSONResponse(content=result)
    except Exception as e:
        msg = e.args.__str__()
        if 'Comanda não encontrada' in msg:
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail=msg)
        else:
            print(traceback.format_exc())
            raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR)

@app.post("/comandas")
def post_comanda(
    session: SessionDep,
    comanda: ComandaPostDTO
):
    """
    Adiciona uma comanda no banco, fazendo o vínculo dos produtos e usuário durante o processo.
    
    Atributos do usuário:
    - **id_usuario**: Identificador do usuário a qual essa comanda pertence.
    - **nome_usuario**: Nome do usuário a qual essa comanda pertence.
    - **telefone_usuario**: Telefone do usuário a qual essa comanda pertence.
    
    Atributos do(s) produto(s):    
    - **id**: Identificador único do produto.
    - **nome**: Nome do produto.
    - **preco**: Preço do produto (formato: 0.00).
    """
    try:
        result = cadastrar_comanda(comanda, session)
        return result
    except Exception as e:
        msg = e.args.__str__()
        if 'produto de id' in msg or 'Não foi possível' in msg:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail=msg)
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.put("/comandas/{id}")
def put_comanda_by_id(
    id: int,
    produtos: List[ProdutoPutDTO],
    session: SessionDep
):
    """
    Altera os produtos de uma comanda.
    
    **Atenção:** Só é possível alterar produtos já existentes na comanda. Não é possível adicionar nem remover produtos através desse método.
    
    Atributos do(s) produto(s) a ser(em) alterado(s):
    - **id**: Identificador único do produto.
    - **nome**: Nome do produto.
    - **preco**: Preço do produto (formato: 0.00).
    """
    try:
        result = alterar_comanda(id, produtos, session)
        return result
    except Exception as e:
        print(e.with_traceback())
        msg = e.args.__str__()
        if 'A comanda não' in msg or 'Comanda não encontrada' in msg:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail=msg)
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.delete("/comandas/{id}")
def delete_comanda_by_id(
    id: int,
    session: SessionDep,
):
    """
    Exclui uma comanda, desfazendo os vínculos de usuário e produto com a comanda.
    - **id**: Identificador da comanda.
    """
    try:
        remover_comanda(id, session)
        return JSONResponse({"success":{"text":"comanda removida"}})
    except Exception as e:
        msg = e.args.__str__()
        if 'Comanda não encontrada' in msg:
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail=msg)
        else:
            print(traceback.format_exc())
            raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR)
