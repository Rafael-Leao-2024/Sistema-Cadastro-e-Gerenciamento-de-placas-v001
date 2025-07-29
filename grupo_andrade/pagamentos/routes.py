from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import extract
import mercadopago
import os
from grupo_andrade.models import Placa, Pagamento
from grupo_andrade.main import db
from grupo_andrade.utils.pagamento_utils import verificar_status_pagamento
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
    
    quantidade = len(placas)
    valor_total = quantidade * 100
    valor_total_str = f'{valor_total:,.2f}'
    
    PROD_ACCESS_TOKEN = os.getenv('PROD_ACCESS_TOKEN')
    sdk = mercadopago.SDK(PROD_ACCESS_TOKEN)
    
    link_resposta_pagamento = "https://127.0.0.1:5000/resultado_pagamento"

    preference_data = {
        "items": [
            {   
                "id": current_user.id,
                "title": f"Pagamento de {quantidade} placas",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": valor_total,
            }
        ],
        "back_urls": {
            "success": f"{link_resposta_pagamento}",  # OBRIGATÓRIO
            "failure": f"{link_resposta_pagamento}",
            "pending": f"{link_resposta_pagamento}",
        },

        "auto_return": "all",
        # Remova notification_url para desenvolvimento local ou use ngrok
        # "notification_url": "https://seu-url-publico.com/notifications"
    }

    preference_response = sdk.preference().create(preference_data)
    try:
        init_point = preference_response["response"]["init_point"]
    except:
        init_point = '/'
    print(preference_response)
    flash(category='success', message="relatorios automatizados com sucesso!")
    return render_template("pagamentos/relatorio_resultados.html", 
                         placas=placas, mes=mes, ano=ano, 
                         quantidade=quantidade, valor_total=valor_total_str,
                         init_point=init_point)

                         
@pagamentos.route('/resultado_pagamento')
@login_required
def resultado_pagamento():
    status_pagamento = request.args.get('status', "approved")
    id_usuario = current_user.id  
    id_pagamento = request.args.get('payment_id', 151515)

    if id_pagamento == 'null':
        flash('Voce desistiu do pagamento caso queira falar com suporte chame no zap', 'warning')
        return redirect(url_for('pagamentos.relatorio'))        

    valor_pago, id_pagamento, status_pagamento = verificar_status_pagamento(id_pagamento)
    novo_pagamento = Pagamento(
        id_pagamento=id_pagamento,
        status_pagamento=status_pagamento,
        id_usuario=id_usuario
    )

    db.session.add(novo_pagamento)
    db.session.commit()
    db.session.refresh(novo_pagamento)

    valor = 1000

    if novo_pagamento.status_pagamento == 'approved':
        flash(f'Pagamento de R$ {valor:,.2f} realizado com sucesso', 'success')
    return render_template('pagamentos/resultado_pagamento.html', status_pagamento=status_pagamento, pagamento=novo_pagamento)


