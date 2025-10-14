from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from grupo_andrade.models import User
from grupo_andrade.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from grupo_andrade.main import db, bcrypt, mail
from grupo_andrade.utils.email_utils import enviar_email_reset_senha
from grupo_andrade.utils.email_utils import verificar_email
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        flash(f'{current_user.username} voce ja esta logado e no Home page', 'success')
        return redirect(url_for('placas.solicitar_placas'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'User {user.username.title()} connected online', 'success')
            return redirect(next_page or url_for('placas.solicitar_placas'))
        else:
            flash('email e senha invalido', 'danger')
    return render_template('auth/login.html', form=form, titulo='login')

@auth.route("/logout")
def logout():
    logout_user()
    flash(f'Voce esta desconectado', 'error')
    return redirect(url_for('auth.login'))

@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        if not verificar_email(form.email.data):
            flash(f'Email nao valido use um email exitente', 'info')
            return redirect(url_for('auth.register'))
    if current_user.is_authenticated:
        flash(f'{current_user.username} Voce ja esta logado e resgristrado pode postar', 'info')
        return redirect(url_for('placas.solicitar_placas'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, data_criacao=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {user.username} Success!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, titulo='register')

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('placas.solicitar_placas'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            enviar_email_reset_senha(user)
            flash('Um e-mail foi enviado com instrucoes para redefinir sua senha.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('usuario nao encontrado ', 'info')
            return redirect(url_for(request.url))
    return render_template('auth/reset_request.html', title='Reset Password', form=form)

@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('placas.solicitar_placas'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Sua senha foi atualizada! Agora voce pode fazer login', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)