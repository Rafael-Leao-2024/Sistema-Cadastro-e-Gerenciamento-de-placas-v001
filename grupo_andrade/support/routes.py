from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from grupo_andrade.support.llm import initialize_chatbot
from grupo_andrade.support.llm_memory import conversa_memoria
from grupo_andrade.support.llm_tools import agent_ferramenta

support = Blueprint('support', __name__, url_prefix='/support')

retriever, chain = initialize_chatbot()

chain_memoria = conversa_memoria()

chain_ferramenta = agent_ferramenta()  


@support.route('/chat')
@login_required
def chat():
    return render_template('support/chat.html')


@support.route('/question', methods=['POST'])
def ask_question():
    data = request.get_json()
    pergunta = data['question']
    
    try:
        contextos = retriever.invoke(pergunta)
        contexto = "\n".join(
            f"Source: {ctx.metadata}\n\nContent: {ctx.page_content}" 
            for ctx in contextos
        )
        resposta_agente = chain_ferramenta.invoke(pergunta)
        
        # resposta = chain.invoke({"context": contexto, "question": pergunta})
        resposta_memoria = chain_memoria.invoke(input={"input": resposta_agente.get('input'), "contexto_retriver": contexto, "contexto_agente_executor": resposta_agente.get('output')}, config={'configurable': { 'session_id': current_user.id}})
        return jsonify({"response": resposta_memoria})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500