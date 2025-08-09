from sqlmodel import select
from models import Comanda

def get_comanda_by_id(id, session):
    return session.exec(select(Comanda)
            .where(Comanda.id == id)
            ).first()

def get_all_comandas(limit, session):
    return session.exec(select(Comanda)
            .limit(limit)
            ).all()

def add_comanda(comanda: Comanda, session):
    session.add(comanda)
    session.commit()

def delete_comanda(comanda: Comanda, session):
    session.delete(comanda)
    session.commit()