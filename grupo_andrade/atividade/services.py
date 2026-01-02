from grupo_andrade.models import Atividade
from grupo_andrade.main import db


def registrar_atividade(usuario_id, acao, descricao=None):
    atividade = Atividade(
        usuario_id=usuario_id,
        acao=acao,
        descricao=descricao
    )
    db.session.add(atividade)
    db.session.commit()
