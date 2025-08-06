from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from datetime import datetime
from bs4 import BeautifulSoup

from grupo_andrade.pagamentos.routes import relatorio_resultados
from grupo_andrade.models import Placa, User

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
    return informacoes
    

@tool
def faturamento_relatorio_placas(mes_referente):
    """"descricao: funcao para pegar relatorio de placas e ver o valor total de faturamento
caso queiram "meu debito " , "relatorio", "soliciacoes "  "pedidos" e etc .
argumentos: mes_referente type(inteiro) Exemplo 7 julho
retorno informacoes em TEXTO
    """
    ano_referente = datetime.now().year
    html_resposta = relatorio_resultados(mes=mes_referente, ano=ano_referente)
    soup = BeautifulSoup(html_resposta, "html.parser")
    return soup.body.main.get_text().replace("\n", "").replace("  ", "")
    



tools = [informacao_placa, faturamento_relatorio_placas]

def agent_ferramenta():
    agent = initialize_agent(
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        llm=ChatOpenAI(temperature=0.5, model_name="gpt-4o"),
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
       )
    return agent

