from langchain_openai import ChatOpenAI  
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser  
from langchain_community.chat_message_histories import SQLChatMessageHistory  
from dotenv import load_dotenv
from flask_login import current_user
import os


load_dotenv()

sistema = """
Voce e Jasmine, uma assistente virtual do Grupo Andrade. Seja direta, amigavel e extremamente concisa 
(no maximo 3 frases por resposta). 

📌 Regras essenciais:
1. Sempre seja humano 
2. Responda APENAS com o contexto fornecido 
3. Seja específica sobre prazos, documentos e valores quando perguntado
4. use emojis nas respostas a cada duas resposta.
5. use informacao de  resultados "resposta_do_agente_para_LLM" para melhor esclarecimento de ferramentas 

tenha atençao nesses tres contexto
contexto de ferramentas:
\n{contexto_ferramentas}\n

Contexto_retriver:
\n{contexto_retriver}
---------------------\n

contexto do nome da pessoa:
\n{current_user_input}\n
"""

prompt = ChatPromptTemplate.from_messages([("system", sistema),
                                           MessagesPlaceholder(variable_name='history'),
                                            ("human", "{input}")])

# persistir todas as conversas baseadas em sessao do usuario em um banco de dados SQL  
def get_session_history_db(session_id):  
    return SQLChatMessageHistory(session_id, connection=os.environ.get("DATABASE_URL")) 


# crie uma funcao de janela de buffer de memoria para retornar as ultimas K conversas  
def memory_window(messages, k=30):  
    return messages[-(k+1):]


def conversa_memoria():
# crie uma cadeia LLM simples que usa apenas as ultimas K conversas  
    chatgpt = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

    llm_chain = (RunnablePassthrough.assign(history=lambda x: memory_window(x["history"]))  
                | prompt  
                | chatgpt  
                | StrOutputParser()) 

    # crie uma cadeia de conversacao para lidar com o historico baseado em sessao.  
    conv_chain = RunnableWithMessageHistory(
        llm_chain,
        get_session_history_db,
        input_messages_key="input",
        history_messages_key="history",
        prompt=prompt
        )

    return conv_chain

