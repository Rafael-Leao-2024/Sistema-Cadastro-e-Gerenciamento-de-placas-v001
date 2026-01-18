from pydantic import BaseModel

class Nota(BaseModel):
    chave_acesso: str

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
    quantidade_produto: int
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
