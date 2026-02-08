from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from grupo_andrade.loja.forms import LojaForm
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user
from grupo_andrade.models import User, Loja, db
from grupo_andrade.atividade.services import registrar_atividade

loja_bp = Blueprint('loja', __name__, url_prefix='/lojas')

@loja_bp.route("/mostrar-lojas")
@login_required
def mostrar_lojas():
    """Listar todas as lojas com seus vendedores"""
    
    # Buscar todas as lojas com seus usuários
    lojas = Loja.query.options(
        db.joinedload(Loja.usuarios)
    ).order_by(Loja.nome).all()
    
    # Calcular estatísticas
    lojas_ativas = sum(1 for loja in lojas if loja.ativa)
    total_vendedores = User.query.filter(User.loja_id.isnot(None)).count()
    
    return render_template('loja/mostrar_lojas.html',
                         lojas=lojas,
                         total_vendedores=total_vendedores,
                         lojas_ativas=lojas_ativas,
                         title='Gerenciar Lojas')



@loja_bp.route('/criar_loja', methods=['GET', 'POST'])
@login_required
def criar_loja():
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('placas.homepage'))
    
    form = LojaForm()
    
    if form.validate_on_submit():
        try:
            # Criar nova loja
            nova_loja = Loja(
                nome=form.nome.data.strip(),
                cnpj=form.cnpj.data if form.cnpj.data else None,
                ativa=form.ativa.data
            )
            
            db.session.add(nova_loja)
            db.session.commit()
            
            flash(f'Loja "{nova_loja.nome}" criada com sucesso!', 'success')
            return redirect(url_for('loja.mostrar_lojas'))  # Ou redirecionar para gerenciamento
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar loja: {str(e)}', 'danger')
            return redirect(url_for('loja.criar_loja'))
    
    # Se GET ou validação falhar, mostrar formulário
    return render_template('loja/criar_loja.html', 
                         form=form, 
                         title='Criar Nova Loja')

@loja_bp.route('/lojas-editar/<int:loja_id>', methods=['GET', 'POST'])
@login_required
def editar_loja(loja_id):
    """Editar uma loja existente"""
    if not current_user.is_admin:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('placas.homepage'))
    
    loja = Loja.query.get_or_404(loja_id)
    form = LojaForm()
    
    # Preencher form com dados existentes
    if request.method == 'GET':
        form.nome.data = loja.nome
        form.cnpj.data = loja.cnpj
        form.ativa.data = loja.ativa
    
    if form.validate_on_submit():
        try:
            loja.nome = form.nome.data.strip()
            loja.cnpj = form.cnpj.data if form.cnpj.data else None
            loja.ativa = form.ativa.data
            
            db.session.commit()
            flash('Loja atualizada com sucesso!', 'success')
            return redirect(url_for('loja.mostrar_lojas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar loja: {str(e)}', 'error')
    
    return render_template('loja/editar_loja.html', 
                         form=form, 
                         loja=loja,
                         title=f'Editar Loja - {loja.nome}')


@loja_bp.route('/lojas/<int:loja_id>/usuarios')
@login_required
def loja_usuarios(loja_id):
    loja = Loja.query.filter(Loja.id == loja_id).first()

    usuarios = User.query.filter_by(loja_id = loja_id).all()

    for usuario in usuarios:
        usuario.total_placas = len(usuario.placas)

    # Buscar usuários sem loja para adicionar
    usuarios_sem_loja = User.query.filter(
        (User.loja_id.is_(None)) | (User.loja_id == 0)
    ).all()

    return render_template('loja/loja_usuarios.html',
                         loja=loja,
                         usuarios=usuarios,
                         usuarios_sem_loja=usuarios_sem_loja,
                         title=f'Usuários - {loja.nome}')

@loja_bp.route('/lojas/<int:loja_id>/adicionar_usuario/<int:usuario_id>')
@login_required
def adicionar_usuario_loja(loja_id, usuario_id):
    loja = Loja.query.get_or_404(loja_id)
    
    usuario = User.query.get_or_404(usuario_id)

    if not loja.ativa:
        flash(f'Loja inativa para adicionar vendedor', 'info')
        return redirect(url_for('loja.loja_usuarios', loja_id=loja_id))

    usuario.loja_id = loja_id
    db.session.commit()

    flash(f'Usuário {usuario.username} adicionado à loja {loja.nome}', 'success')
    return redirect(url_for('loja.loja_usuarios', loja_id=loja_id))


@loja_bp.route('/lojas/<int:loja_id>/remover_usuario/<int:usuario_id>')
@login_required
def remover_usuario_loja(loja_id, usuario_id):
    """Remover usuário de uma loja"""
    usuario = User.query.get_or_404(usuario_id)
    
    if usuario.loja_id != loja_id:
        flash('Usuário não pertence a esta loja', 'error')
        return redirect(url_for('loja.loja_usuarios', loja_id=loja_id))
    
    usuario.loja_id = None
    db.session.commit()
    
    flash(f'Usuário {usuario.username} removido da loja', 'info')
    return redirect(url_for('loja.loja_usuarios', loja_id=loja_id))