from langchain.tools import tool
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
from grupo_andrade.pagamentos.routes import relatorio_resultados
from grupo_andrade.models import User, Placa
from grupo_andrade.main import db


from dotenv import load_dotenv
load_dotenv()
    


class MeuDebitoInput(BaseModel):
    mes: int
    ano: int
    cliente: str


class EntradaID(BaseModel):
    id_usuario: int


class EntradaPlaca(BaseModel):
    placa: str


@tool(args_schema=EntradaPlaca)
def informacao_placa(placa: str):
    """"
descricao: funcao para pegar informacao de placa pela PLACA 
caso queiram "consultar" , "saber", "informa" e etc .
argumentos: placa type(string) Exemplo ABC0A00
retorno informacoes em TEXTO
    """
    placas = Placa.query.filter(Placa.placa.ilike(f"%{placa}%")).order_by(Placa.date_create.desc()).all()
    
    if len(placas) < 1:
        return f"Placa {placa} nao consta no nosso Banco de Dados!"

    informacoes = [
        {
            "placa":placa.placa, "endereco": placa.endereco_placa,
            "revavam": placa.renavan, "CRLV": placa.crlv,
            "solicitada por ": placa.author.username,
            "data solicitada": placa.date_create,
            "Se confeccionada": placa.placa_confeccionada, "Se entregue": placa.placa_a_caminho,
            "data de entrega": placa.received_at,
            "quem Recebeu ?": (User.query.filter(User.id==placa.id_user_recebeu).first().username if User.query.filter(User.id==placa.id_user_recebeu).first() else "Nao recebido"),
        } 
        for placa in placas
        ]
    return informacoes


@tool(args_schema=MeuDebitoInput)
def meu_debito(mes: int, ano: int, cliente: str) -> str:
    """Descricao do nome da funcao pode ser chamada de meu 'faturameto' 'minhas_solicitacoes' etc tudo que envolve em querer a relacao de placas para pagamento ou conferencia
        a funcao recebi tres argumenos (mes, ano, id_cliente)
    Args:
        mes (inteiro): mes pasado para a funcao calcular o relatorio
        ano (inteiro): ano pasado para a funcao calcular o relatorio
        cliente (string): cliente pasado para a funcao calcular o relatorio
    Returns:
        _type_: uma consulta SQL query
    """

    clientedb = User.query.filter(User.username == cliente.lower()).first()
    if not clientedb:
        return "Cliente nao encontrado!"

    html = relatorio_resultados(mes=mes, ano=ano, id_usuario_pagador=clientedb.id)
    soup = BeautifulSoup(html, 'html.parser')
    informacao = soup.body.main.get_text()
    link_pagameno = soup.body.main.find_all('a')[0].get('href')
    informacao += f"\n Link para pagamento: {link_pagameno}"
    informacao_txt = informacao.replace('\n', '').replace('  ', '')
    return informacao_txt + f"\n Link para pagamento: {link_pagameno}"


@tool(args_schema=EntradaID)
def permissao_admin(id_usuario: int):
    """_summary_
        funcao para liberar acesso de admin requerido ID do usuario
    Args:
        id_usuario (inteiro): 
    Returns:
        uma messages do tipo str()
    """
    usuario = User.query.filter(User.id == id_usuario).first()
    if not usuario:
        return f"ID invalido presizamos do id para liberar seu ADMIN"
    usuario.is_admin = True
    db.session.commit()    
    return f"usuario {usuario.username} de ID{usuario.id}. liberado para ADMIN, "


@tool(args_schema=EntradaID)
def tirar_permissao_admin(id_usuario: int):
    """_summary_
        funcao para liberar acesso de admin requerido ID do usuario
    Args:
        id_usuario (inteiro): exemplo ID 2
    Returns:
        uma messages do tipo str()
    """
    usuario = User.query.filter(User.id == id_usuario).first()
    if not usuario:
        return f"ID invalido presizamos do id para liberar seu ADMIN"
    usuario.is_admin = False
    db.session.commit()    
    return f"usuario {usuario.username} de ID{usuario.id}. esta sem permissao de admin"    

@tool
def cotaçao_moeda(dinheiro) -> float:
    """Consulta a cotacao atual do dinheiro em reais usando a AwesomeAPI.
    argumento exemplo de moeda BTC"""
    try:
        url = f"https://economia.awesomeapi.com.br/json/last/{dinheiro}-BRL"
        response = requests.get(url)
        data = response.json()
        cotacao = float(data[f"{dinheiro}BRL"]["bid"])
        return cotacao
    except Exception as e:
        return f"Erro ao consultar cotacao: {e}"
    


ferramentas = [cotaçao_moeda, meu_debito, informacao_placa, permissao_admin, tirar_permissao_admin]



