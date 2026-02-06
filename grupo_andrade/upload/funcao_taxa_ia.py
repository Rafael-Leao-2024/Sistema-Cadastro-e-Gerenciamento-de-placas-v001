from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

class PlacaSchema(BaseModel):
    placa: str = Field(description="numeraçao de placa do veiculo ")
    chassi: str = Field(description="o chassi é 17 caractere ex 95BO151R484RGC844 e começa sempre com numero nao confunda com numero de motor pois e parecido")


class Taxa(BaseModel):
    descricao: str 
    valor: float
    codigo_barra:str

class Boleto(BaseModel):
    taxas: List[Taxa]
    veiculo: PlacaSchema



def extrator_taxa_ia(texto):
     
    # 🔧 Configurar modelo (use sua API KEY)
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"), temperature=0)  # pode usar gpt-4o, gpt-5, etc.
    parser = PydanticOutputParser(pydantic_object=Boleto)


    prompt = PromptTemplate(
        template = """
Você é um especialista EXTREMAMENTE experiente em leitura e interpretação de boletos do DETRAN
(DAE, IPVA, multas, RENAINF, SSP-PCR).

Sua tarefa é analisar um texto de boleto NÃO ESTRUTURADO e identificar corretamente as TAXAS.

REGRAS IMPORTANTES :

1️⃣ Os VALORES das taxas SEMPRE aparecem NO INÍCIO do texto do boleto,
antes de qualquer descrição detalhada.

2️⃣ As DESCRIÇÕES das taxas aparecem SOMENTE após o texto:
   "DISCRIMINAÇÃO DOS DÉBITOS" use exatamente o mesmo nome da descriçao

4️⃣ associe automaticamente valores às infrações listadas se o boleto
informar explicitamente o valor individual de cada uma.

7️⃣ IGNORE campos como:
    - Mora Multa
    - Prêmio Líquido
    - IOF
    - Prêmio Total
    - VALOR COBRADO

FORMATO DE SAÍDA (OBRIGATÓRIO):
- Retorne EXCLUSIVAMENTE no formato abaixo
- descricao: string (descrição clara da taxa)
- valor: float (valor numérico, sem símbolos, vírgula convertida para ponto)
- codigo_barra = linha digitável completa apenas com números ex 
- remova espaços e hífens do código de barras 

{format_instructions}

TEXTO DO BOLETO:
--------------------
{texto}


    """,
        input_variables=["texto"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    

    chain = prompt | llm | parser
    resultado = chain.invoke({"texto": texto})
    return resultado 
