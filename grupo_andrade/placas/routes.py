from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

from grupo_andrade.placas.forms import EmplacamentoForm, ConsultarForm, PlacaStatusForm, EmplacamentoUpdateForm
from grupo_andrade.utils.email_utils import enviar_email_confirmacao_placa
from grupo_andrade.models import Placa, Endereco, User
from grupo_andrade.main import db



placas = Blueprint('placas', __name__)

@placas.route("/")
def homepage():
    flash(message="Pagina Principal", category="success")
    return render_template('homepage.html', titulo='homepage')

@placas.route("/todas")
def todas():
    per_page = 10
    page = request.args.get('page', 1, type=int)
    placas = Placa.query.options(joinedload(Placa.author))\
                    .order_by(desc(Placa.date_create))\
                    .paginate(page=page, per_page=per_page, error_out=False)
    total_placas = Placa.query.count()
    return render_template('placas/todas.html', placas=placas, total_placas=total_placas, titulo='todas')

@placas.route("/minhas-placas")
@login_required
def minhas_placas():
    per_page = 10
    page = request.args.get('page', 1, type=int)
    placas = Placa.query.options(joinedload(Placa.author))\
               .filter_by(id_user=current_user.id)\
               .order_by(desc(Placa.date_create))\
               .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('placas/minhas_placas.html', placas=placas, titulo='minhas placas')

@placas.route('/minhas-placas/<int:placa_id>', methods=['GET', 'POST'])
@login_required
def placa_detail(placa_id):
    form = EmplacamentoForm()
    placa = Placa.query.filter_by(id=placa_id).first()
    if placa is None:
        flash(message="placa nao encontrada", category="info")
        return redirect(url_for('placas.minhas_placas'))
    usuario = User.query.filter_by(id=placa.id_user_recebeu).first()
    usuario_solicitante = User.query.filter_by(id=placa.id_user).first()
    if not placa.id_user == current_user.id:
        if not current_user.is_admin:
            return render_template('erros/erro.html')
    
    if request.method == 'POST':
        received = request.form.get('received') == 'on'
        if received and not placa.received:
            placa.id_user_recebeu = current_user.id
            placa.received = True
            placa.received_at = datetime.now()
            flash(f"Placa {placa.placa.upper()} Recebida com sucesso.", 'success')
        elif not received and placa.received:
            time_limit = placa.received_at + timedelta(minutes=10)
            if datetime.now() <= time_limit:
                placa.id_user_recebeu = current_user.id
                placa.received = False
                placa.received_at = None  
            else:
                flash("Não é possível desmarcar após 10 minutos.", 'info')
        db.session.commit()
        return redirect(url_for('placas.placa_detail', placa_id=placa.id))   
    
    return render_template('placas/placa_detail.html', placa=placa, form=form, titulo='detalhes', usuario=usuario, usuario_solicitante=usuario_solicitante)

@placas.route("/minhas-placas/<int:placa_id>/delete", methods=['GET', 'POST'])
@login_required
def delete(placa_id):
    placa = Placa.query.get_or_404(placa_id)
    if placa.author != current_user and current_user.email != "rafaelampaz6@gmail.com":
        flash("Você não tem permissão para deletar esta placa.", "warning")
        return redirect(url_for('placas.minhas_placas'))

    time_limit = placa.date_create + timedelta(hours=24)
    if datetime.now() > time_limit:
        flash("Você só pode deletar placas criadas há menos de 24 horas.", "error")
        return redirect(url_for('placas.minhas_placas'))

    db.session.delete(placa)
    db.session.commit()
    flash(f'Sua placa {placa.placa.upper()} foi deletada!', 'success')
    return redirect(url_for('placas.minhas_placas'))

@placas.route('/consulta', methods=['GET', 'POST'])
@login_required
def consulta():
    resultados = []
    form = ConsultarForm()
    if request.method == 'POST':
        placa = request.form.get('placa')
        placa = placa.upper()
        if placa:
            resultados = Placa.query.filter(Placa.placa.ilike(f"%{placa}%")).order_by(Placa.date_create.desc()).all()
            if not resultados:
                flash("Placa não encontrada!", "warning")
            else:
                flash(f"Resultados Encontrados {len(resultados)}", "success")
    return render_template('placas/consulta.html', resultados=resultados, form=form)

@placas.route('/editar/<int:placa_id>', methods=['GET', 'POST'])
@login_required
def editar_placa(placa_id):
    form = EmplacamentoUpdateForm()
    placa = Placa.query.filter(Placa.id == placa_id).first()
    if not placa:
        flash(f"placa de ID {placa_id} nao existe.", "info")
        return redirect(url_for('placas.minhas_placas'))

    if placa.id_user != current_user.id:
        if not current_user.is_admin:
            flash("Você não tem permissão para editar esta placa.", "danger")
            return redirect(url_for('placas.placa_detail', placa_id=placa.id))

    if request.method == 'POST':
        placa.placa = request.form.get('placa')
        placa.renavan = request.form.get('renavan')
        placa.endereco_placa = request.form.get('endereco_placa')
        placa.crlv = request.form.get('crlv')
        db.session.commit()
        flash(f"Os dados da placa {placa.placa.upper()} foram atualizados com sucesso!", "success")
        return redirect(url_for('placas.placa_detail', placa_id=placa.id))

    return render_template('placas/editar_placa.html', placa=placa, form=form, placa_id=placa.id)

@placas.route('/solicitar_placas', methods=['GET', 'POST'])
@login_required
def solicitar_placas():
    if request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        try:
            endereco = endereco.endereco.title()
        except:
            endereco = Endereco.endereco.default.arg
    
    if request.method == 'POST':
        placas = request.form.getlist('placa') 
        enderecos = request.form.getlist('endereco_placa') 
        crlvs = request.form.getlist('crlv')
        renavams = request.form.getlist('renavam')

        lista_placas = []
        for placa, endereco, crlv, renavam in zip(placas, enderecos, crlvs, renavams):
            nova_placa = Placa(
                placa=placa.upper(),
                endereco_placa=endereco, 
                crlv=crlv, renavan=renavam,
                id_user=current_user.id
                )
            db.session.add(nova_placa)
            lista_placas.append(nova_placa)        
        db.session.commit()
        
        if len(lista_placas) > 0:
            enviar_email_confirmacao_placa(current_user, lista_placas)  
            flash('Placas solicitadas com sucesso e e-mail enviado!', 'success')
            return redirect(url_for('placas.minhas_placas'))
        else:
            flash('Voce não preencheu os campos com os dados!', 'info')
            return redirect(url_for('placas.solicitar_placas'))        
    return render_template('placas/solicitar_placas.html', titulo='solicitar varias placas', endereco=endereco)

@placas.route("/gerenciamento-pedidos")
@login_required
def gerenciamento_pedidos():
    page = request.args.get('page', 1, type=int)
    placas = Placa.query.options(joinedload(Placa.author))\
                       .order_by(desc(Placa.date_create))\
                       .paginate(page=page, per_page=10, error_out=False)
    form = PlacaStatusForm()
    return render_template('placas/status_manager_placas.html', placas=placas, titulo='gerenciamento', tamanho=placas.total, form=form, page=page)


def pegar_pagina(referer):
    if not referer:
        return '1'  # Retorna 1 se não houver Referer ou for vazio
    
    # Verifica se há 'page=' ou 'pagina=' no URL
    page_param = None
    for param in ['page=', 'pagina=']:
        if param in referer:
            page_param = param
            break
    
    if not page_param:
        return '1'  # Retorna 1 se não encontrar o parâmetro
    
    # Pega a parte do URL depois do parâmetro
    start_index = referer.index(page_param) + len(page_param)
    substring = referer[start_index:]
    
    # Pega apenas os dígitos (número da página)
    page_number = []
    for char in substring:
        if char.isdigit():
            page_number.append(char)
        else:
            break  # Para no primeiro caractere não numérico
    
    return ''.join(page_number) if page_number else '1'


@placas.route("/gerenciamento-pedidos/<int:id_placa>", methods=['GET', 'POST'])
@login_required
def gerenciamento_final(id_placa):
    form = PlacaStatusForm()
    placa = Placa.query.filter(Placa.id==id_placa).first()
    page = int(pegar_pagina(dict(request.headers).get('Referer')))
    # page = 1
    print(form.placa_confeccionada.data)
    print(form.placa_a_caminho.data)
    print(form.data.get("placa_a_caminho"))
    print(form.data.get("placa_confeccionada"))
    print(form.data)

    
    if request.method == "POST":
        if current_user.is_admin:
            if form.validate_on_submit():
                # Botão de placa confeccionada
                if 'placa_confeccionada' in request.form:
                    placa.placa_confeccionada = form.placa_confeccionada.data
                
                # Botão de placa a caminho
                if 'placa_a_caminho' in request.form:
                    placa.placa_a_caminho = form.placa_a_caminho.data
                
                # Outros botões podem ser adicionados de forma similar
                db.session.commit()
            flash(category="success", message="checkbox valido")
        else:
            flash(category="danger", message="Voce nao tem permissao de ADMIN")   
    return redirect(url_for('placas.gerenciamento_pedidos', page=page))
