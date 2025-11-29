from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

from grupo_andrade.placas.forms import EmplacamentoForm, ConsultarForm, PlacaStatusForm, EmplacamentoUpdateForm
from grupo_andrade.utils.email_utils import enviar_email_confirmacao_servivos
from grupo_andrade.models import Placa, Endereco, User, Notificacao
from grupo_andrade.main import db
from flask import current_app, g
from grupo_andrade.models import Notificacao


placas = Blueprint('placas', __name__)


def injetar_notificacao():
    g.notificacoes_nao_lidas = 0
    if current_user.is_authenticated and current_user.is_admin:
        g.notificacoes_nao_lidas = Notificacao.query.filter_by(id_usuario=current_user.despachante ,lida=False).count()
    return (dict(notificacoes_nao_lidas=g.notificacoes_nao_lidas))



@placas.context_processor
def inject_notificacoes_placas():
    return injetar_notificacao()



@placas.route("/")
def homepage():
    flash(message="Pagina Principal", category="success")
    return render_template('homepage.html', titulo='homepage')


@placas.route("/todas")
@login_required
def todas():
    usuarios = User.query.filter(User.despachante==current_user.id).all()
    per_page = 10
    page = request.args.get('page', 1, type=int)
    placas = Placa.query.filter(Placa.id_user.in_([user.id for user in usuarios])).options(joinedload(Placa.author))\
                .order_by(desc(Placa.date_create))\
                .paginate(page=page, per_page=per_page, error_out=False)
    total_placas = placas.total
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
            placa.received_at = datetime.utcnow()
            flash(f"Placa {placa.placa.upper()} Recebida com sucesso.", 'success')
        elif not received and placa.received:
            time_limit = placa.received_at + timedelta(minutes=10)
            if datetime.now() <= time_limit:
                placa.id_user_recebeu = current_user.id
                placa.received = False
                placa.received_at = None
                placa.id_user_recebeu = None
            else:
                flash("Nao e possivel desmarcar apos 10 minutos.", 'info')
        db.session.commit()
        return redirect(url_for('placas.placa_detail', placa_id=placa.id))    
    return render_template('placas/placa_detail.html', placa=placa, form=form, titulo='detalhes', usuario=usuario, usuario_solicitante=usuario_solicitante)

@placas.route("/minhas-placas/<int:placa_id>/delete", methods=['GET', 'POST'])
@login_required
def delete(placa_id):
    placa = Placa.query.get(placa_id)
    if placa.author != current_user and current_user.email != "rafaelampaz6@gmail.com":
        flash("Voce nao tem permissão para deletar esta placa.", "warning")
        return redirect(url_for('placas.minhas_placas'))

    time_limit = placa.date_create + timedelta(hours=24)
    if datetime.now() > time_limit:
        flash("Voce so pode deletar placas criadas ha menos de 24 horas.", "error")
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
        chassi = request.form.get('chassi')
        if chassi:
            resultados = Placa.query.filter(Placa.chassi.ilike(f"%{chassi.upper()}%")).order_by(Placa.date_create.desc()).all()
            if not resultados:
                flash("Placa nao encontrada!", "warning")
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
            flash("Voce nao tem permissao para editar esta placa.", "danger")
            return redirect(url_for('placas.placa_detail', placa_id=placa.id))

    if request.method == 'POST':
        placa.placa = request.form.get('placa')
        placa.chassi = request.form.get('chassi')
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
    despachante = "Sem despachante"

    if request.method == "POST" and not current_user.despachante:
        flash('Selecione um despachante antes!', 'dange')
        return redirect(url_for('placas.solicitar_placas'))
    
    if current_user.despachante:
        despachante_user = User.query.filter_by(id=current_user.despachante).first()
        if despachante_user:
            despachante = despachante_user.username.title()
    if request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        placa = Placa.query.filter_by(id_user=current_user.id).order_by(Placa.id.desc()).first()
        try:
            endereco = endereco.rua.title()
            placa = placa.placa.title()
        except:
            endereco = Endereco.rua.default.arg
            placa = Placa.placa.default.arg
    
    if request.method == 'POST':
        chassis = request.form.getlist('chassi')
        placas = request.form.getlist('placa')
        enderecos = request.form.getlist('endereco_placa') 
        crlvs = request.form.getlist('crlv')
        renavams = request.form.getlist('renavam')

        lista_placas = []
        for chassi, placa, endereco, crlv, renavam in zip(chassis, placas, enderecos, crlvs, renavams):
            nova_placa = Placa(
                placa=placa.upper(),
                chassi=chassi.upper(),
                endereco_placa=endereco, 
                crlv=crlv, renavan=renavam,
                id_user=current_user.id
                )
            db.session.add(nova_placa)
            lista_placas.append(nova_placa)    
        db.session.commit()
        db.session.refresh(nova_placa)
        
        mensagem = f"{current_user.username.title()} Solicitou.{len(lista_placas)} data e hora {nova_placa.date_create}"
        if len(lista_placas) > 1:
            mensagem = F"""{current_user.username.title()} Solicitou varios serviços total {len(lista_placas)} data e hora {nova_placa.date_create}"""

        notificacao = Notificacao(
            mensagem=mensagem,
            id_solicitacao=nova_placa.id,
            id_usuario=current_user.despachante,
        )

        db.session.add(notificacao)
        db.session.commit()

        if len(lista_placas) == 1:
            flash('Solicitaçao enviada com sucesso!', 'success')
            return redirect(url_for('documentos.upload_file_anexo', id_placa=lista_placas[0].id))
        
        if len(lista_placas) > 1:
            enviar_email_confirmacao_servivos(current_user, lista_placas)
            flash('Solicitaçao enviada com sucesso e e-mail enviado!', 'success')
            return redirect(url_for('placas.minhas_placas'))
        
        else:
            flash('Voce nao preencheu os campos com os dados!', 'info')
            return redirect(url_for('placas.solicitar_placas'))     
    return render_template('placas/solicitar_placas.html', titulo='solicitar varias placas', endereco=endereco, placa=placa, despachante=despachante)

@placas.route('/notificacoes')
@login_required
def pegar_notificacoes():
    # pegar todas minhas notificacoes
    minhas_notificacoes = Notificacao.query.filter_by(id_usuario=current_user.id, lida=False).order_by(desc(Notificacao.data_criacao)).all()
    # transformar em lista de dicionarios pra enviar pro js
    notificacoes = []

    for notif in minhas_notificacoes:
        notificacoes.append({
        'id': notif.id,
        'mensagem': notif.mensagem,
        'data_criacao': notif.data_criacao.strftime('%d/%m/%Y %H:%M'),
        'lida': notif.lida,
        
        })
    
    return jsonify(notificacoes)

# Rota para marcar notificação como lida
@placas.route('/marcar-lida/<int:notificacao_id>', methods=['POST'])
@login_required
def marcar_como_lida(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    notificacao.lida = True
    db.session.commit()
    flash('Notificacao marcada como lida.', 'success')
    return jsonify({'success': True})


# Rota para marcar todas como lidas
@placas.route('/marcar-todas-lidas', methods=['POST'])
@login_required
def marcar_todas_lidas():
    # todas minhas notificacoes pra marcar como lida
    minhas_notificacoes = Notificacao.query.filter_by(id_usuario=current_user.id, lida=False).all()
    if not minhas_notificacoes:
        return jsonify({'success': False, 'message': 'Nenhuma notificacao nao lida encontrada.'})   
    for notif in minhas_notificacoes:
        notif.lida = True

    db.session.commit()
    flash('Todas as notificacoes marcadas como lidas.', 'success')
    # retorne para mesma pagina atual
    return jsonify({'success': True})



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
