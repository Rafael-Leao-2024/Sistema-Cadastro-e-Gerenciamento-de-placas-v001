from flask import Blueprint, render_template, request, jsonify
from grupo_andrade.support.llm import initialize_chatbot

support = Blueprint('support', __name__, url_prefix='/support')

retriever, chain = initialize_chatbot()

@support.route('/chat')
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
        
        resposta = chain.invoke({"context": contexto, "question": pergunta})
        return jsonify({"response": resposta})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500