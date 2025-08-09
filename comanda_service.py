from comanda_repo import *
from comanda_produto_repo import *
from usuario_repo import *
from produto_repo import *
from models import ComandaPostDTO, ProdutoPutDTO, Produto

def buscar_comandas(limit, session):
    comandas = get_all_comandas(limit, session)

    usuarios = []
    for comanda in comandas:
        usuarios.append(get_usuario_by_id(comanda.id_usuario, session))

    result = []
    for usuario in usuarios:
        result.append({
            "idUsuario": usuario.id,
            "nomeUsuario": usuario.nome,
            "telefoneUsuario": usuario.telefone,
        })
    
    return result

def buscar_comanda_by_id(id, session, showId = False):
    comanda = get_comanda_by_id(id, session)
    if not comanda:
        raise Exception("Comanda não encontrada")

    produtosIds = get_produtos_ids_by_comanda_id(id, session)
    
    produtos = get_produtos_by_ids(produtosIds, session)

    produtosFinais = []

    for produto in produtos:
        produtosFinais.append({
            "id": produto.id,
            "nome": produto.nome,
            "preco": produto.preco
        })

    usuario = get_usuario_by_id(comanda.id_usuario, session)

    result = {
            "id": id,
            "idUsuario": usuario.id,
            "nomeUsuario": usuario.nome,
            "telefoneUsuario": usuario.telefone,
            "produtos": produtosFinais
        } if showId else {
            "idUsuario": usuario.id,
            "nomeUsuario": usuario.nome,
            "telefoneUsuario": usuario.telefone,
            "produtos": produtosFinais
        }

    return result

def cadastrar_comanda(comanda: ComandaPostDTO, session):
    produtos = comanda.produtos
    for produto in produtos:
        produtoCheck = get_produto_by_id(produto.id, session)
        if not produtoCheck:
            produto.preco = round(produto.preco, 2)
            dbProduto = Produto.from_orm(produto)
            session.add(dbProduto)
        elif produtoCheck.nome != produto.nome or produtoCheck.preco != produto.preco:
            raise Exception("O produto de id "+produto.id.__str__()+" já está cadastrado, porém seu nome e/ou preço estão diferentes na requisição.")
    session.commit()
    
    usuarioCheck = get_usuario_by_id(comanda.id_usuario, session)
    usuarioCheck2 = get_usuario_by_nome_and_telefone(comanda.nome_usuario, comanda.telefone_usuario, session)

    if not usuarioCheck:
        addedUsuario = Usuario(
            id=comanda.id_usuario,
            nome=comanda.nome_usuario,
            telefone=comanda.telefone_usuario
        )
        add_usuario(addedUsuario, session)

    elif usuarioCheck2:
        comanda.id_usuario = usuarioCheck2.id
        
    elif usuarioCheck and (usuarioCheck.nome != comanda.nome_usuario or usuarioCheck.telefone != comanda.telefone_usuario):
        addedUsuario = Usuario(
            nome=comanda.nome_usuario,
            telefone=comanda.telefone_usuario
        )
        add_usuario(addedUsuario, session)
        comanda.id_usuario = addedUsuario.id

    dbProdutos = []
    for produto in produtos:
        dbProdutos.append(get_produto_by_id(produto.id, session))
    
    addedComanda = Comanda(id_usuario=comanda.id_usuario)
    add_comanda(addedComanda, session)

    for dbProduto in dbProdutos:
        addedComandaProduto = Comanda_Produto(id_comanda=addedComanda.id, id_produto=dbProduto.id)
        add_comanda_produto(addedComandaProduto, session)
    return buscar_comanda_by_id(addedComanda.id, session, True)

def alterar_comanda(id, produtos: ProdutoPutDTO, session):
    comanda = get_comanda_by_id(id, session)

    if not comanda:
        raise Exception("Comanda não encontrada")

    produtosIds = [p.id for p in produtos]
    dbProdutos = get_produtos_by_ids(produtosIds, session)
    produtosIds = {p.id for p in dbProdutos}
    for produto in produtos:
        if produto.id not in produtosIds:
            raise Exception("A comanda não possui um produto com o id: "+produto.id.__str__())
        dbProduto = Produto(nome=produto.nome, preco=round(produto.preco,2))
        session.add(dbProduto)
    session.commit()
    
    return buscar_comanda_by_id(id, session)

def remover_comanda(id, session):
    comanda = get_comanda_by_id(id, session)
    if not comanda:
        raise Exception("Comanda não encontrada")

    comandaProdutos = get_comanda_produtos_by_comanda_id(id, session)
    produtosIds = []
    for comandaProduto in comandaProdutos:
        produtosIds.append(comandaProduto.id_produto)
        delete_comanda_produto(comandaProduto, session)
    for produtoId in produtosIds:
        produtoCheck = get_comanda_produtos_by_produto_id(produtoId, session)
        if not produtoCheck:
            dbProduto = get_produto_by_id(produtoId, session)
            delete_produto(dbProduto, session)

    delete_comanda(comanda, session)