from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Taxa(BaseModel):
    descricao: str = Field(description="Descrição clara do débito", min_length=3)
    valor: float = Field(description="Valor do débito em reais")


class Boleto(BaseModel):
    taxas: List[Taxa]


from PyPDF2 import PdfReader


def lendo_boleto(arquivo_pdf) -> str:
    reader = PdfReader(arquivo_pdf)
    texto = "\n".join(page.extract_text() or "" for page in reader.pages)
    return texto


def deduplicar_taxas(taxas):
    valores = {}
    resultado = []

    for taxa in taxas:
        valor = round(taxa.valor, 2)

        if valor in valores:
            # já existe taxa com esse valor → ignora
            continue

        valores[valor] = taxa.descricao
        resultado.append(taxa)

    return resultado


def extrator_taxa_ia(texto):
    # 🔧 Configurar modelo (use sua API KEY)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # pode usar gpt-4o, gpt-5, etc.
    parser = PydanticOutputParser(pydantic_object=Boleto)

    prompt = PromptTemplate(
    template = """
Você é um EXTRATOR CONTÁBIL DE BOLETOS DE VEÍCULOS (DETRAN / SEFAZ).

OBJETIVO:
Extrair débitos reais do veículo, garantindo associação correta
entre descrição e valor.

REGRAS CRÍTICAS (OBRIGATÓRIAS):
- Cada taxa DEVE ter:
  1) UMA descrição específica
  2) UM valor monetário correspondente
- Se UMA descrição estiver associada a MAIS DE UM valor no texto:
  → trate como TAXAS DISTINTAS
  → diferencie a descrição de forma clara e objetiva

EXEMPLO OBRIGATÓRIO:
Se aparecer:
"CONTROLE E EMISSÃO DE ORDEM DE EMPLACAMENTO"
com valores:
47,20
224,25

Você DEVE retornar:
- "Controle e Emissão de Ordem de Emplacamento" → 47.20
- "Taxa de Emplacamento" → 224.25

NÃO REPITA:
- A MESMA descrição com valores diferentes
- O MESMO valor com a mesma descrição

DEDUPLICAÇÃO OBRIGATÓRIA:
- Se o mesmo débito (descrição + valor) aparecer mais de uma vez no texto,
  retorne APENAS UMA vez.

IGNORE COMPLETAMENTE:
- Totais
- Valor cobrado
- Linhas digitáveis
- ISOF
- Prêmio líquido / total
- Mora / multa
- Acréscimos
- Campos 0,00

REGRAS DE SEGURANÇA:
- NÃO deduza valores
- NÃO some
- NÃO invente taxas inexistentes
- Se não conseguir diferenciar a descrição corretamente → NÃO retorne a taxa

FORMATO DE SAÍDA:
{format_instructions}

TEXTO:
{texto}
"""
,
    input_variables=["texto"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

    chain = prompt | llm | parser
    return chain.invoke({"texto": texto})
