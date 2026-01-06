from flask import Blueprint, render_template, redirect, url_for, flash, request, url_for
from flask_login import login_required, current_user
from PIL import Image
import secrets
import os

from grupo_andrade.users.forms import EnderecoForm, UpdateAccountForm
from grupo_andrade.models import User, Endereco
from grupo_andrade.main import db

users = Blueprint('users', __name__)

@users.route('/endereco', methods=['GET', 'POST'])
@login_required
def endereco():
    form = EnderecoForm()
    if request.method == 'POST':
        cidade = request.form['cidade']
        rua = request.form['rua']
        bairro = request.form['bairro']
        cep = request.form['cep']
        uf = request.form['uf']
        novo_endereco = Endereco(cidade=cidade, rua=rua, id_user=current_user.id, bairro=bairro, cep=cep, uf=uf)
        db.session.add(novo_endereco)
        db.session.commit()
        flash('Endereco Atualizado com Sucesso!', 'success')
        return redirect(url_for('users.endereco'))
    elif request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        if endereco:
            form.cidade.data = "" if not endereco.cidade else endereco.cidade.title()
            form.rua.data = "" if not endereco.rua else endereco.rua.title()
            form.bairro.data = endereco.bairro.title() if endereco.bairro else ""
            form.cep.data = endereco.cep if endereco.cep else ""
            form.uf.data = endereco.uf.upper() if endereco.uf else ""

    return render_template('users/endereco.html', form=form, endereco=endereco)

@users.route('/usuarios')
@login_required
def listar_usuarios():
    usuarios = User.query.order_by(User.data_criacao.desc())
    usuarios_clientes = usuarios.filter(User.despachante == current_user.id).all()
    return render_template('users/listar_usuarios.html', usuarios=usuarios_clientes)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('grupo_andrade/static/profile_pics', picture_fn)
    output_size = (125, 125)
    imagem = Image.open(form_picture)
    imagem.thumbnail(output_size)
    imagem.save(picture_path)
    return picture_fn

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.rg = form.rg.data
        current_user.cpf_cnpj = form.cpf_cnpj.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.rg.data = current_user.rg
        form.cpf_cnpj.data = current_user.cpf_cnpj
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('users/account.html', title='Account', form=form, image_file=image_file)


@users.route("/usuario/<int:user_id>", methods=['GET', 'POST'])
@login_required
def info_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        flash(f"Usuario de ID: {user_id} nao encontrado ", "info")
        return redirect(url_for("users.listar_usuarios"))
    return render_template('users/info_user.html', user=user)


@users.route("/usuario/<int:user_id>/delete", methods=['GET', 'POST'])
@login_required
def deletar_usuario(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        flash('Usuario nao encontro ', 'info')
        return redirect(url_for('users.info_user', user_id=user_id))
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {user.username} deletado', 'success')
    return redirect(url_for('users.info_user', user_id=user_id))