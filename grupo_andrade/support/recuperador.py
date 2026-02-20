from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os


load_dotenv()


def recuperador_documentos():
    # caminho_pdf = os.path.abspath(__file__)
    # caminho_diretorio = os.path.dirname(caminho_pdf)
    # caminho_completo = os.path.join(caminho_diretorio, "servicos_de_veiculos.pdf")
    # loader = PyPDFLoader(caminho_completo)
    # documentos_pages = loader.load()
    
    # # Split dos documentos
    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=1000, 
    #     chunk_overlap=50,
    #     separators=["\n", "\n\n"]
    # )
    
    # documents_splits = splitter.split_documents(documentos_pages)
    
    # # Cria o vectorstore
    # vectorstore = FAISS.from_documents(documents_splits, OpenAIEmbeddings())
    # retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    return {}#retriever