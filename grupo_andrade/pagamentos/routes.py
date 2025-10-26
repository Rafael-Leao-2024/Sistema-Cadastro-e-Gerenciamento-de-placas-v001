from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import extract
from grupo_andrade.models import Placa, Pagamento, User
from grupo_andrade.main import db
from grupo_andrade.utils.pagamento_utils import verificar_status_pagamento, criar_preferencia
from dotenv import load_dotenv
from grupo_andrade.placas.routes import injetar_notificacao
from datetime import datetime

load_dotenv()


pagamentos = Blueprint('pagamentos', __name__)

@pagamentos.context_processor
def inject_notificacoes_pagamentos():
    return injetar_notificacao()


@pagamentos.route("/relatorio", methods=["GET", "POST"])
@login_required
def relatorio():
    pagadores = User.query.filter(User.despachante == current_user.id).all()
    if request.method == "POST":
        mes = int(request.form.get("mes"))
        ano = int(request.form.get("ano"))
        id_usuario_pagador = int(request.form.get("id_usuario_pagador"))  # Novo campo
        return redirect(url_for('pagamentos.relatorio_resultados', mes=mes, ano=ano, id_usuario_pagador=id_usuario_pagador))
    flash(category='info', message="relatorios automatizados")
    if not pagadores:
        pagadores += [current_user]
    return render_template("pagamentos/relatorio_form.html", current_year=datetime.now().year, pagadores=pagadores)


@pagamentos.route("/relatorio/<int:mes>/<int:ano>/<int:id_usuario_pagador>")
@login_required
def relatorio_resultados(mes, ano, id_usuario_pagador):
    print(id_usuario_pagador)
    # Query base
    query = Placa.query.filter(
        Placa.id_user == id_usuario_pagador,
        extract("month", Placa.date_create) == mes,
        extract("year", Placa.date_create) == ano
    )
    
    # Filtro por pagador específico se não for "Todos"
    if id_usuario_pagador != 0:
        query = query.filter(Placa.id_user == id_usuario_pagador)
        
    
    placas = query.all()
    
    try:
        total, init_point = criar_preferencia(placas=placas)
    except:
        init_point, total = '/', 0
    
    # Buscar informações do pagador selecionado
    pagador_selecionado = None
    if id_usuario_pagador != 0:
        pagador_selecionado = User.query.get(id_usuario_pagador)
    
    print(total, init_point)
    print(id_usuario_pagador)
    print(placas)
    flash(category='success', message="relatorios automatizados com sucesso!")
    return render_template("pagamentos/relatorio_resultados.html", 
                         placas=placas, mes=mes, ano=ano, 
                         quantidade=len(placas), valor_total=total,
                         init_point=init_point,
                         pagador_selecionado=pagador_selecionado,
                         id_usuario_pagador=id_usuario_pagador)

                         
@pagamentos.route('/resultado_pagamento')
@login_required
def resultado_pagamento():
    id_pagamento = request.args.get('payment_id')
    if id_pagamento == 'null' or id_pagamento == None:
        flash('Voce desistiu do pagamento caso queira falar com suporte chame no zap', 'warning')
        return redirect(url_for('pagamentos.relatorio'))        

    valor_pagamento, id_pagamento, status_pagamento = verificar_status_pagamento(id_pagamento)

    pagamento = Pagamento(id_pagamento=id_pagamento, status_pagamento=status_pagamento,
                           id_usuario=current_user.id, valor_transacao=valor_pagamento)

    db.session.add(pagamento)
    db.session.commit()
    db.session.refresh(pagamento)

    if pagamento.status_pagamento == 'approved':
        flash(f'Pagamento de R$ {valor_pagamento:,.2f} realizado com sucesso!', 'success')
    elif pagamento.status_pagamento == 'canceled':
        flash(f'Pagamento de R$ {valor_pagamento:,.2f} foi cancelado!', 'danger')
    else:
        flash(f'Pagamento de R$ {valor_pagamento:,.2f} esta Pendente!', 'warning')

    return render_template('pagamentos/resultado_pagamento.html', status_pagamento=status_pagamento, pagamento=pagamento)


