from PyPDF2 import PdfReader
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

class Nota(BaseModel):
    chave_acesso: str = Field(description="uma serie de numeros bem cumprido")

class Remetente(BaseModel):
    nome_remetente: str
    cnpj_remetente: str
    cidade_remetente: str
    uf_remetente: str

class Destinatario(BaseModel):
    nome_destinatario: str
    cnpj_destinatario: str
    endereco_destinatario: str
    bairro_destinatario: str
    cep_destinatario: str
    cidade_destinatario: str
    uf_destinatario: str

class Produto(BaseModel):
    nome_produto: str
    quantidade_produto: str
    valor_unitario_produto: str
    valor_total_nota: str
    chassi: str
    cor_produto: str
    numero_motor:str
    ano_modelo: str
    ano_fabricacao: str


class DadosCompleto(BaseModel):
    nota : Nota
    remetente: Remetente
    destinatario: Destinatario
    produto: Produto




def ler_pdf(file):
    reader = PdfReader(file)    
    texto = reader.pages[0].extract_text()
    return texto


def gerador_saida_estruturada(texto):
        # 🔧 Configurar modelo (use sua API KEY)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # pode usar gpt-4o, gpt-5, etc.
    parser = PydanticOutputParser(pydantic_object=DadosCompleto)

    prompt = PromptTemplate(
        template="""Voce é um especialista contabil com esperiencia em notas fiscais.
Extraia os dados da NOTA FISCAL abaixo e retorne EXCLUSIVAMENTE no formato estruturado.
nao invente as informaçoes se nao souber deixe em branco
{format_instructions}

TEXTO DA NOTA FISCAL
    --------------------
    {texto}
    """,
        input_variables=["texto"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    resultado = chain.invoke({"texto": texto})
    return resultado

