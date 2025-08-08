from sqlmodel import select
from models import Produto

def get_produto_by_id(id, session):
    return session.exec(select(Produto)
            .where(Produto.id == id)
            ).first()

def get_produtos_by_ids(produtosIds, session):
    return session.exec(select(Produto)
            .where(Produto.id.in_(produtosIds))
            ).all()

def create_produto(produto: Produto, session):
    session.add(produto)
    session.commit()
    session.refresh(produto)