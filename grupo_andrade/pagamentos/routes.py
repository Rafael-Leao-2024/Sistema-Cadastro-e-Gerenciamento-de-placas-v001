from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from sqlalchemy import extract
from grupo_andrade.models import Placa, Pagamento, User
from grupo_andrade.main import db
from grupo_andrade.utils.pagamento_utils import verificar_status_pagamento, criar_preferencia
from dotenv import load_dotenv
from grupo_andrade.placas.routes import injetar_notificacao
from datetime import datetime
from sqlalchemy import extract, func
from grupo_andrade.atividade.services import registrar_atividade
from io import BytesIO
import pandas as pd

load_dotenv()


pagamentos = Blueprint('pagamentos', __name__)

@pagamentos.context_processor
def inject_notificacoes_pagamentos():
    return injetar_notificacao()



@pagamentos.route("/financas-geral", methods=["POST", "GET"])
@login_required
def financas_geral():
    # Pegar todos os usuários
    usuarios = User.query.filter(User.despachante == current_user.id).all()
    if not usuarios:
        usuarios = User.query.filter(User.id == current_user.id).all()
    
    # Para cada usuário, buscar os dados agrupados
    usuarios_com_dados = []
    
    for usuario in usuarios:
        # Consulta específica para este usuário
        placas_agrupadas = db.session.query(
            extract('year', Placa.date_create).label('ano'),
            extract('month', Placa.date_create).label('mes'),
            func.count(Placa.id).label('total_placas'),
            func.sum(Placa.honorario).label('total_honorario')
        ).filter(
            Placa.author == usuario
        ).group_by(
            extract('year', Placa.date_create),
            extract('month', Placa.date_create)
        ).order_by(
            extract('year', Placa.date_create).desc(),
            extract('month', Placa.date_create).desc()
        ).all()
        
        # Calcular totais
        total_placas = sum([p.total_placas or 0 for p in placas_agrupadas])
        total_honorario = sum([float(p.total_honorario or 0) for p in placas_agrupadas])
        
        usuarios_com_dados.append({
            'usuario': usuario,
            'placas_agrupadas': placas_agrupadas,
            'total_placas': total_placas,
            'total_honorario': total_honorario
        })
    
    # Ordenar usuários por total de honorários (decrescente)
    usuarios_com_dados.sort(key=lambda x: x['total_honorario'], reverse=True)
    
    return render_template('pagamentos/geral_financa.html', 
                         usuarios=usuarios_com_dados, now=datetime.now())


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


@pagamentos.route('/exportar-placas/<int:mes>/<int:ano>/<int:id_usuario_pagador>')
def exportar_placas(mes, ano, id_usuario_pagador):
    pessoa = User.query.filter(User.id == id_usuario_pagador).first().username

    placas = Placa.query.filter(
        Placa.id_user == id_usuario_pagador,
        extract("month", Placa.date_create) == mes,
        extract("year", Placa.date_create) == ano
    ).all()

    dados = []

    for p in placas:
        dados.append({
            'Data Criaçao': p.date_create.strftime('%d/%m/%Y %H:%M'),
            'Placaa': p.placa,
            'Chassi': p.chassi,
            'Solicitantes': User.query.filter(User.id == p.id_user).first().username,
            'Proprietarios': p.nome_proprietario,
            'Honorarios': p.honorario,
            'NFs': p.chave_acesso,
            'Data emissao NFs': p.data_emissao_nf,
            'Status': 'Finalizado' if  p.placa_a_caminho else 'Pendente',
            'Totais Taxas': sum(boleto.total_taxas() for boleto in p.boletos)
        })
    
    df = pd.DataFrame(data=dados)
    print(df)

    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Placas")
    output.seek(0)

    return send_file(
        output,
        download_name=f'Relatorio mensal {pessoa} {mes}-{ano}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@pagamentos.route("/relatorio/<int:mes>/<int:ano>/<int:id_usuario_pagador>")
@login_required
def relatorio_resultados(mes, ano, id_usuario_pagador):
    if id_usuario_pagador == 0:
        flash("Selecione um usuario")
        return redirect(url_for("pagamentos.relatorio"))        
    # Query base
    placas = Placa.query.filter(
        Placa.id_user == id_usuario_pagador,
        extract("month", Placa.date_create) == mes,
        extract("year", Placa.date_create) == ano
    ).all()
    
    try:
        total, init_point = criar_preferencia(placas=placas)
    except:
        init_point, total = '/', 0
    
    # Buscar informações do pagador selecionado
    pagador_selecionado = None
    if id_usuario_pagador != 0:
        pagador_selecionado = User.query.get(id_usuario_pagador)

    registrar_atividade(
        usuario_id=current_user.id,
        acao="PAGAMENTO",
        descricao=f'{current_user.username.upper()} pesquisou finanças de {pagador_selecionado.username.upper()} mes-({mes}), total R${total}'
    )

    flash(category='success', message="relatorios automatizados com sucesso!")
    return render_template("pagamentos/relatorio_resultados.html", 
                         placas=placas, mes=mes, ano=ano, 
                         quantidade=len(placas), valor_total=round(total, 2),
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


