from flask import Blueprint, render_template, redirect, url_for
from grupo_andrade.placas.routes import injetar_notificacao
from grupo_andrade.models import Atividade, User
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from datetime import datetime


atividade = Blueprint("atividade", __name__, url_prefix="/atividade")

@atividade.context_processor
def inject_notificacoes_support():
    return injetar_notificacao()


@atividade.route("/todas-atividades")
@login_required
def todas_atividades():
    usuarios = User.query.filter(User.despachante == current_user.despachante).all()
    atividades = Atividade.query.filter(Atividade.usuario_id.in_([user.id for user in usuarios])).options(joinedload(Atividade.author))\
        .order_by(Atividade.data.desc()).all()[:50]

    return render_template("atividade/atividades.html", atividades=atividades)


@atividade.route('/detalhe-atividade/<int:id_atividade>', methods=['POST', 'GET'])
@login_required
def detalhe_atividade(id_atividade: int):
    atividade = Atividade.query.filter(Atividade.id == id_atividade).first()
    if not atividade:
        return redirect(url_for('atividade.todas_atividades'))
    return render_template("atividade/detalhe_atividade.html", atividade=atividade, now=datetime.now())

