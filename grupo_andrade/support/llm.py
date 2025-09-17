from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

template = """
Você é Jasmine, a assistente virtual do Grupo Andrade. Seja direta, amigável e extremamente concisa 
(no máximo 3 frases por resposta). 

📌 Regras essenciais:
1. Sempre seja humano
2. Responda APENAS com o contexto fornecido
3. Seja específica sobre prazos, documentos e valores quando perguntado
4. use emojis para melhor visualidade

Contexto: {context}

Pergunta: {question}
---
"""

def initialize_chatbot():
    # Carrega o PDF
    caminho_pdf = r"C:\Users\rafae\Documents\Sistema-Cadastro-e-Gerenciamento-de-placas-v001\grupo_andrade\support\servicos_de_veiculos.pdf"
    loader = PyPDFLoader(caminho_pdf)
    documentos_pages = loader.load()
    
    # Split dos documentos
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=50,
        separators=["\n", "\n\n"]
    )
    
    documents_splits = splitter.split_documents(documentos_pages)
    
    # Cria o vectorstore
    vectorstore = FAISS.from_documents(documents_splits, OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    # Configura a chain
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")
    chain = prompt | llm | StrOutputParser()
    
    return retriever, chain