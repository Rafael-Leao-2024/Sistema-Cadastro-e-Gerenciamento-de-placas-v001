from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv 

load_dotenv()


class Proprietario(BaseModel):
    nome: str = Field(description='nome é o nome do proprietario do veiculo pode ser pessoal ou secretario ou instituiçoes ministerios orgao do governo e etc.')
    cpf: str
    cidade: str
    uf: str


class Veiculo(BaseModel):
    codigo_renavam : str
    placa: str = Field(description="numeraçao de placa do veiculo ")
    numero_do_crv: str
    chassi: str = Field(description="o chassi é 17 caractere ex 95BO151R484RGC844 e começa sempre com numero nao confunda com numero de motor pois e parecido")


class SchemaDados(BaseModel):
    veiculo: Veiculo
    proprietario : Proprietario


def leitor_crlv_ia(input):
    parser = PydanticOutputParser(pydantic_object=SchemaDados)

    prompt = PromptTemplate(
    template="""
    Antes de responder:
- Verifique o tamanho EXATO de cada campo
- Se não bater o tamanho, retorne vazio ""
- NÃO chute valores parecidos
- NÃO use número de motor como chassi
- NÃO use CRV como renavam
- Se houver dúvida → campo vazio

Extraia APENAS os dados solicitados no formato estruturado.

⚠️ REGRAS IMPORTANTES (OBRIGATÓRIO SEGUIR):
- Nao confunda o numero do CRV com o codigo renavam REGRAS:
- O renavan ta sempre logo apos a frase "Leia o QR Code e baixe agora."
- CODIGO RENAVAM tem EXATAMENTE  dígitos numéricos. Pegue somente este número.
- O NUMERO DO CRV tem EXATAMENTE  (doze) dígitos numéricos. Pegue somente este número o crv vem logo apos a PLACA.
- Placa segue o padrão brasileiro mercosul: 7 caracteres , PLACA esta logo apos o renavam.
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