from usuario_repo import *
from models import UsuarioDTO, Usuario

def cadastrar_usuario(usuario: UsuarioDTO, session):
    if get_usuario_by_nome_or_telefone(usuario.nome, usuario.telefone, session):
        raise Exception("Usuário já existe")

    if get_usuario_by_id(usuario.id, session):
        addedUsuario = Usuario(nome=usuario.nome, telefone=usuario.telefone)
        add_usuario(addedUsuario, session)
    else:
        addedUsuario = Usuario.from_orm(usuario)
        add_usuario(addedUsuario, session)