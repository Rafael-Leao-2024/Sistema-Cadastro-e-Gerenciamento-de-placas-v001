from flask import Blueprint, render_template, redirect, url_for, flash, request, url_for
from flask_login import login_required, current_user
from PIL import Image
import secrets
import os
from grupo_andrade.models import User, Endereco
from grupo_andrade.users.forms import EnderecoForm, UpdateAccountForm
from grupo_andrade.main import db

users = Blueprint('users', __name__)

@users.route('/endereco', methods=['GET', 'POST'])
@login_required
def endereco():
    form = EnderecoForm()
    if request.method == 'POST':
        endereco = request.form['endereco']
        novo_endereco = Endereco(endereco=endereco, id_user=current_user.id)
        db.session.add(novo_endereco)
        db.session.commit()
        flash('Endereço Atualizado com Sucesso!', 'success')
        return redirect(url_for('users.endereco'))
    elif request.method == 'GET':
        endereco = Endereco.query.filter_by(id_user=current_user.id).order_by(Endereco.id.desc()).first()
        if endereco:
            form.endereco.data = endereco.endereco.title()
        else:
            form.endereco.data = Endereco.endereco.default.arg
    print(endereco)
    return render_template('users/endereco.html', form=form, endereco=endereco)

@users.route('/usuarios')
def listar_usuarios():
    usuarios = User.query.order_by(User.id.desc()).all()
    return render_template('users/listar_usuarios.html', usuarios=usuarios)

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
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('users/account.html', title='Account', form=form, image_file=image_file)
