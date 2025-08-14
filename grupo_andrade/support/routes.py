from flask import Blueprint, render_template, request, jsonify
from grupo_andrade.support.llm_memory import conversa_memoria
from grupo_andrade.support.llm_tools import agent_ferramenta
from grupo_andrade.support.llm import initialize_chatbot
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationBufferMemory
from flask_login import login_required, current_user
from langchain_core.messages import HumanMessage, SystemMessage


support = Blueprint('support', __name__, url_prefix='/support')

retriever, chain = initialize_chatbot()
chain_ferramenta = agent_ferramenta()
chain_memoria = conversa_memoria()

@support.route('/chat')
@login_required
def chat():
    message_history = SQLChatMessageHistory(session_id=current_user.id, connection_string="sqlite:///memory.db")
    memory = ConversationBufferMemory(chat_memory=message_history, memory_key="chat_history", return_messages=True)
    historicos = memory.buffer_as_messages
    mensagens = [("User", historico) if isinstance(historico, HumanMessage) else ("AI", historico) for historico in historicos]
    if not len(mensagens) > 1:
        mensagens = []
    print(mensagens)           
    return render_template('support/chat.html', mensagens=mensagens)

@support.route('/question', methods=['POST'])
def ask_question():
    data = request.get_json()
    pergunta = data['question']
    
    try:
        contextos = retriever.invoke(pergunta)
        contexto_retriver = "\n".join(
            f"Source: {ctx.metadata}\n\nContent: {ctx.page_content}" 
            for ctx in contextos
        )
        resposta_agente = chain_ferramenta.invoke(pergunta)
        resposta_memoria = chain_memoria.invoke(input={"input": resposta_agente.get('input'), "contexto_retriver": contexto_retriver, "contexto_ferramentas":resposta_agente.get('output')}, config={'configurable': { 'session_id': current_user.id}})
        return jsonify({"response": resposta_memoria})
    
    except Exception as erro:
        return jsonify({"error": str(erro)}), 500