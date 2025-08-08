from sqlmodel import select
from models import Usuario

def get_usuario_by_id(id, session):
    return session.exec(select(Usuario)
                .where(Usuario.id == id)
            ).first()

def get_usuario_by_nome_or_telefone(nome, telefone, session):
    return session.exec(select(Usuario)
                .where(Usuario.nome == nome
                or Usuario.telefone == telefone)
            ).first()

def get_usuario_by_id_nome_or_telefone(id, nome, telefone, session):
    return session.exec(select(Usuario)
                .where(Usuario.id == id
                or Usuario.nome == nome
                or Usuario.telefone == telefone)
            ).first()

def add_usuario(usuario, session):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)