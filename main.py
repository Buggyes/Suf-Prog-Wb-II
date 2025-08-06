from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from sqlmodel import create_engine, Session
from http import HTTPStatus
from sqlmodel import select
from models import *
from services import *

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
def create_usuario(usuario: UsuarioDTO, session: Session = Depends(get_session)):
    expression = select(Usuario).where(Usuario.nome == usuario.nome).where(Usuario.telefone == usuario.telefone)
    result = session.exec(expression).first()
    
    if not result:
        added_usuario = Usuario(nome=usuario.nome, telefone=usuario.telefone)
        session.add(added_usuario)
        session.commit()
        session.refresh(added_usuario)
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Usuário criado com sucesso"})
        
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário já existe")

@app.get("/comandas")
def get_comandas(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    comandas = session.exec(
        select(Comanda).offset(offset).limit(limit)
    ).all()

    result = []

    for comanda in comandas:
        result.append({
            "idUsuario": comanda.idUsuario,
            "nomeUsuario": comanda.nomeUsuario,
            "telefoneUsuario": comanda.telefoneUsuario,
        })
    
    return JSONResponse(content=result)

#TODO: terminar de escrever esse método
@app.get("/comandas/{id}")
def get_comandas(
    id: int,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    comandas = session.exec(
        select(Comanda).offset(offset).limit(limit).where(Comanda.id == id)
    ).all()

    result = []

    for comanda in comandas:
        result.append({
            "idUsuario": comanda.idUsuario,
            "nomeUsuario": comanda.nomeUsuario,
            "telefoneUsuario": comanda.telefoneUsuario,
        })
    
    return JSONResponse(content=result)