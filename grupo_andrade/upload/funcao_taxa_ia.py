from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()


class Taxa(BaseModel):
    descricao: str 
    valor: float

class Boleto(BaseModel):
    taxas: List[Taxa]



def extrator_taxa_ia(texto):
     
    # 🔧 Configurar modelo (use sua API KEY)
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.5)  # pode usar gpt-4o, gpt-5, etc.
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
