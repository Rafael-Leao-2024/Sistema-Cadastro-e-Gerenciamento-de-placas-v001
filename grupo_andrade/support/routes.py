from flask import Blueprint, render_template, request, jsonify, current_app
from grupo_andrade.support.llm_memory import conversa_memoria
from grupo_andrade.support.llm import initialize_chatbot
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationBufferMemory
from flask_login import login_required, current_user
from langchain_core.messages import HumanMessage
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from grupo_andrade.support.llm_tools import ferramentas
from grupo_andrade.placas.routes import injetar_notificacao
import os
from dotenv import load_dotenv

load_dotenv()


support = Blueprint('support', __name__, url_prefix='/support')


@support.context_processor
def inject_notificacoes_support():
    return injetar_notificacao()


retriever, chain = initialize_chatbot()
chain_memoria = conversa_memoria()

def memoria_session(banco_dados):
    message_history = SQLChatMessageHistory(session_id=current_user.id, connection_string=banco_dados)
    memory = ConversationBufferMemory(chat_memory=message_history, memory_key="chat_history", return_messages=True)
    return memory

@support.route('/chat')
@login_required
def chat():
    memory = memoria_session(banco_dados=os.environ.get("DATABASE_URL")  + '?options=-c%20search_path=memory_agent')
    historicos = memory.buffer_as_messages
    mensagens = [("User", historico) if isinstance(historico, HumanMessage) else ("AI", historico) for historico in historicos]
    if not len(mensagens) > 1:
        mensagens = []
    return render_template('support/chat.html', mensagens=mensagens)


def agent_ferramenta(memory):
        agent = initialize_agent(
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        llm=ChatOpenAI(temperature=0.5, model_name="gpt-4o-mini"),
        tools=ferramentas,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
       )
        return agent




@support.route('/question', methods=['POST'])
@login_required
def ask_question():
    memory = memoria_session(banco_dados=os.environ.get("DATABASE_URL")  + '?options=-c%20search_path=memory_agent')
    agente = agent_ferramenta(memory)

    data = request.get_json()
    pergunta = data['question']
    
    try:
        contextos = retriever.invoke(pergunta)
        contexto_retriver = "\n".join(
            f"Content: {ctx.page_content}" 
            for ctx in contextos
        )
        resposta_agente = agente.invoke(pergunta)
        resposta_memoria = chain_memoria.invoke(input={"input": resposta_agente.get('input'), "contexto_retriver": contexto_retriver, "contexto_ferramentas":resposta_agente.get('output')}, config={'configurable': { 'session_id': current_user.id}})
        
        return jsonify({"response": resposta_memoria})
    except Exception as erro:
        return jsonify({"error": str(erro)}), 500