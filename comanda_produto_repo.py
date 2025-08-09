from sqlmodel import select
from models import Comanda_Produto

def get_produtos_ids_by_comanda_id(id, session):
    return session.exec(select(Comanda_Produto.id_produto)
            .where(Comanda_Produto.id_comanda == id)
            ).all()

def get_comanda_produtos_by_comanda_id(id, session):
    return session.exec(select(Comanda_Produto)
            .where(Comanda_Produto.id_comanda == id)
            ).all()

def get_comanda_produtos_by_produto_id(id, session):
    return session.exec(select(Comanda_Produto)
            .where(Comanda_Produto.id_produto == id)
            ).all()

def add_comanda_produto(comandaProduto: Comanda_Produto, session):
    session.add(comandaProduto)
    session.commit()
    session.refresh(comandaProduto)

def delete_comanda_produto(comandaProduto: Comanda_Produto, session):
    session.delete(comandaProduto)
    session.commit()