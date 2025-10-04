from langchain_openai import ChatOpenAI  
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser  
from langchain_community.chat_message_histories import SQLChatMessageHistory  
from dotenv import load_dotenv
import os

load_dotenv()

sistema = """
Você é Jasmine, a assistente virtual do Grupo Andrade. Seja direta, amigável e extremamente concisa 
(no máximo 3 frases por resposta). 

📌 Regras essenciais:
1. Sempre seja humano
2. Responda APENAS com o contexto fornecido 
3. Seja específica sobre prazos, documentos e valores quando perguntado
4. use emojis nas respostas a cada duas resposta.
5. use informaçao de  resultados "resposta_do_agente_para_LLM" para melhor esclarecimento de ferramentas 

contexto de ferramentas:
{contexto_ferramentas}
Contexto_retriver:
{contexto_retriver}
---------------------
"""

prompt = ChatPromptTemplate.from_messages([("system", sistema),
                                           MessagesPlaceholder(variable_name='history'),
                                            ("human", "{input}")])

# persistir todas as conversas baseadas em sessão do usuário em um banco de dados SQL  
def get_session_history_db(session_id):  
    return SQLChatMessageHistory(session_id, connection=os.environ.get("DATABASE_URL_MEMORY", "sqlite:///memory_llm.db")) + f'?options=-c%20search_path=memory_llm'

# crie uma função de janela de buffer de memória para retornar as últimas K conversas  
def memory_window(messages, k=30):  
    return messages[-(k+1):]

def conversa_memoria():
# crie uma cadeia LLM simples que usa apenas as últimas K conversas  
    chatgpt = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    llm_chain = (RunnablePassthrough.assign(history=lambda x: memory_window(x["history"]))  
                | prompt  
                | chatgpt  
                | StrOutputParser()) 

    # crie uma cadeia de conversação para lidar com o histórico baseado em sessão.  
    conv_chain = RunnableWithMessageHistory(
        llm_chain,
        get_session_history_db,
        input_messages_key="input",
        history_messages_key="history",
        )


    return conv_chain

