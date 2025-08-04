from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import requests

@tool
def traducao(str):
    '''
    traduza todo o texto antes de responder, em portugues do brasil'''    
    return str

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


tools = [traducao, cotaçao_moeda]

def agent_ferramenta():
    agent = initialize_agent(
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        llm=ChatOpenAI(temperature=0.5, model_name="gpt-4o"),
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
       )
    return agent

