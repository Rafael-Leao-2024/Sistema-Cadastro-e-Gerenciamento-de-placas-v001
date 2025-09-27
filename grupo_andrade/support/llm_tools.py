from langchain.tools import tool
from bs4 import BeautifulSoup
import requests
from grupo_andrade.pagamentos.routes import relatorio_resultados
from grupo_andrade.models import User
from grupo_andrade.models import Placa
from grupo_andrade.main import db


from dotenv import load_dotenv
load_dotenv()


@tool
def informacao_placa(placa):
    """"
descricao: funcao para pegar informaçao de placa pela PLACA 
caso queiram "consultar" , "saber", "informa" e etc .
argumentos: placa type(string) Exemplo ABC0A00
retorno informacoes em TEXTO
    """
    placas = Placa.query.filter(Placa.placa.ilike(f"%{placa}%")).order_by(Placa.date_create.desc()).all()
    informacoes = [
        {
            "placa":placa.placa, "endereço": placa.endereco_placa,
            "revavam": placa.renavan, "CRLV": placa.crlv,
            "solicitante": placa.author.username,
            "data solicitada": placa.date_create,
            "confeccionada": placa.placa_confeccionada, "entregue": placa.placa_a_caminho,
            "data de entrega": placa.received_at,
            "Recebimento": (User.query.filter(User.id==placa.id_user_recebeu).first().username if User.query.filter(User.id==placa.id_user_recebeu).first() else "Nao recebido"),
        } 
        for placa in placas
        ]
    if len(informacoes) < 1:
        return f"Placa {placa} nao consta no nosso Banco de Dados!"
    return informacoes
    
@tool
def meu_debito(mes):
    """Descriçao do nome da funcao pode ser chamada de meu 'faturameto' 'minhas_solicitacoes' etc tudo que envolve em querer a relacao de placas para pagamento ou conferencia
    Args:
        mes (inteiro): mes pasado para a funcao calcular o relatorio
    Returns:
        _type_: uma consulta SQL query
    """
    html = relatorio_resultados(mes=mes, ano=2025)
    soup = BeautifulSoup(html, 'html.parser')
    informacao = soup.body.main.get_text()
    link_pagameno = soup.body.main.find_all('a')[-2].get('href')
    informacao += f"\n Link para pagamento: {link_pagameno}"
    informacao_txt = informacao.replace('\n', '').replace('  ', '')
    return informacao_txt + f"\n Link para pagamento: {link_pagameno}"


@tool
def permissao_admin(id_usuario):
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


@tool
def tirar_permissao_admin(id):
    """_summary_
        funcao para liberar acesso de admin requerido ID do usuario
    Args:
        id_usuario (inteiro): exemplo ID 2
    Returns:
        uma messages do tipo str()
    """
    usuario = User.query.filter(User.id == id).first()
    if not usuario:
        return f"ID invalido presizamos do id para liberar seu ADMIN"
    usuario.is_admin = False
    db.session.commit()    
    return f"usuario {usuario.username} de ID{usuario.id}. esta sem permissao de admin"    

@tool
def cotaçao_moeda(dinheiro) -> float:
    """Consulta a cotação atual do dinheiro em reais usando a AwesomeAPI.
    argumento exemplo de moeda BTC"""
    try:
        url = f"https://economia.awesomeapi.com.br/json/last/{dinheiro}-BRL"
        response = requests.get(url)
        data = response.json()
        cotacao = float(data[f"{dinheiro}BRL"]["bid"])
        return cotacao
    except Exception as e:
        return f"Erro ao consultar cotação: {e}"


ferramentas = [cotaçao_moeda, meu_debito, informacao_placa, permissao_admin, tirar_permissao_admin]



