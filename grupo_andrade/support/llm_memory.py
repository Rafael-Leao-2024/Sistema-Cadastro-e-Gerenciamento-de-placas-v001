# from langchain_groq import ChatGroq  
from langchain_openai import ChatOpenAI  
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  
from langchain_core.output_parsers import StrOutputParser  
from langchain_community.chat_message_histories import SQLChatMessageHistory  
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory

from dotenv import load_dotenv

load_dotenv()

sistema = """
Você é Jasmine, a assistente virtual do Grupo Andrade. Seja direta, amigável e extremamente concisa 
(no máximo 3 frases por resposta). 

📌 Regras essenciais:
1. Sempre seja humano
2. Responda APENAS com o contexto fornecido
3. Seja específica sobre prazos, documentos e valores quando perguntado
4. use emojis nas respostas a cada duas resposta.


Contexto_retriver: {contexto_retriver}
---------------------
resultado de ferramentas simples composto:{contexto_agente_executor}
Contexto_agente_executor: {contexto_agente_executor}

"""

prompt = ChatPromptTemplate.from_messages([("system", sistema),
                                           MessagesPlaceholder(variable_name='history'),
                                            ("human", "{input}")])

# persistir todas as conversas baseadas em sessão do usuário em um banco de dados SQL  
def get_session_history_db(session_id):  
    return SQLChatMessageHistory(session_id, connection="sqlite:///memory.db") 

# crie uma função de janela de buffer de memória para retornar as últimas K conversas  
def memory_window(messages, k=30):  
    return messages[-(k+1):]

def conversa_memoria():
# crie uma cadeia LLM simples que usa apenas as últimas K conversas  
    chatgpt = ChatOpenAI(model_name="gpt-4o", temperature=0)

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

