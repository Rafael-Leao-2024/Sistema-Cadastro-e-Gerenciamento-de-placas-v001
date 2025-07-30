from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import extract
import mercadopago
import os
from grupo_andrade.models import Placa, Pagamento
from grupo_andrade.main import db
from grupo_andrade.utils.pagamento_utils import verificar_status_pagamento, criar_preferencia
from dotenv import load_dotenv

load_dotenv()


pagamentos = Blueprint('pagamentos', __name__)

@pagamentos.route("/relatorio", methods=["GET", "POST"])
@login_required
def relatorio():
    if request.method == "POST":
        mes = int(request.form.get("mes"))
        ano = int(request.form.get("ano"))
        return redirect(url_for('pagamentos.relatorio_resultados', mes=mes, ano=ano))
    flash(category='info', message="relatorios automatizados")
    return render_template("pagamentos/relatorio_form.html", current_year=2025)



@pagamentos.route("/relatorio/<int:mes>/<int:ano>")
@login_required
def relatorio_resultados(mes, ano):
    placas = Placa.query.filter(
        Placa.id_user == current_user.id,
        extract("month", Placa.date_create) == mes,
        extract("year", Placa.date_create) == ano
    ).all()
        
    try:
        total, init_point = criar_preferencia(placas=placas)
    except:
        init_point, total = '/', 0

    flash(category='success', message="relatorios automatizados com sucesso!")
    return render_template("pagamentos/relatorio_resultados.html", 
                         placas=placas, mes=mes, ano=ano, 
                         quantidade=len(placas), valor_total=total,
                         init_point=init_point)

                         
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
    else:
        flash(f'Pagamento de R$ {valor_pagamento:,.2f} esta Pendente!', 'warning')

    return render_template('pagamentos/resultado_pagamento.html', status_pagamento=status_pagamento, pagamento=pagamento)


