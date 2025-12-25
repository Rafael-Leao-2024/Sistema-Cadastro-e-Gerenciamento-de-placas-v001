from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv 
from PyPDF2 import PdfReader

load_dotenv()

class Proprietario(BaseModel):
    nome: str
    cpf: str
    cidade: str
    uf: str

class Veiculo(BaseModel):
    renavan : str = Field(description="o codigo renavam e a numeraçao antes da numeraçao da placa")
    placa: str = Field(description="- Placa segue o padrão brasileiro: 7 caracteres (ex: ABC1D23).")
    crlv: str = Field(description="o crlv sao sempre a sequencia de 12 numeros")
    chassi: str = Field(description="o chassi é 17 caractere ex 95BO151R484RGC844 e começa sempre com numero nao confunda com numero de motor pois e parecido")


class SchemaDados(BaseModel):
    veiculo: Veiculo
    proprietario : Proprietario


def gerador_saida_estruturada(input):
    parser = PydanticOutputParser(pydantic_object=SchemaDados)

    prompt = PromptTemplate(
    template="""
Extraia APENAS os dados solicitados no formato estruturado.

⚠️ REGRAS IMPORTANTES (OBRIGATÓRIO SEGUIR):
- RENAVAM tem EXATAMENTE 11 dígitos numéricos. Pegue somente este número.
- CRLV tem EXATAMENTE 12 dígitos numéricos. Pegue somente este número.
- Placa segue o padrão brasileiro: 7 caracteres (ex: ABC1D23).
- Chassi tem EXATAMENTE 17 caracteres, misto de letras e números.
- NÃO invente valores. Se não estiver no texto, deixe vazio.
- O texto pode estar desordenado (PDF extraído). Use padrões, não posições.

Caso nao saiba nao invente deixe em branco ("")

{format_instructions}

TEXTO DO DOCUMENTO:
--------------------
{input}
""",
    input_variables=["input"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

    modelo = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chain = prompt | modelo | parser

    resultado = chain.invoke({"input": input})

    return resultado

def ler_pdf(file):
    reader = PdfReader(file)
    page = reader.pages[0]
    return page.extract_text()