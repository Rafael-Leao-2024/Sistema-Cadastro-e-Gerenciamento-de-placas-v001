from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()


class Vendedor(BaseModel):
    nome_vendedor : str
    cpf_cnpj_vendedor: str
    cidade_vendedor: str
    uf_vendedor: str

class Comprador(BaseModel):
    nome_comprador : str
    cpf_cnpj_comprador: str
    cidade_comprador: str
    uf_comprador: str

class Veiculo(BaseModel):
    chassi: str = Field(description="o chassi é 17 caractere ex 95BO151R484RGC844 e começa sempre com numero nao confunda com numero de motor pois e parecido")
    vendedor : Vendedor
    comprador : Comprador


def leitor_atpv_ia(texto):
    # 🔧 Configurar modelo (use sua API KEY)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)  # pode usar gpt-4o, gpt-5, etc.
    parser = PydanticOutputParser(pydantic_object=Veiculo)

    prompt = PromptTemplate(
        template="""
    Extraia os dados de DOCUMENTOS ATPV abaixo e retorne EXCLUSIVAMENTE no formato estruturado.
    nao invente as informaçoes se nao souber deixe em branco

    {format_instructions}

    TEXTO DO ATPV:
    --------------------
    {texto}
    """,
        input_variables=["texto"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    veiculo = chain.invoke({"texto": texto})

    return veiculo