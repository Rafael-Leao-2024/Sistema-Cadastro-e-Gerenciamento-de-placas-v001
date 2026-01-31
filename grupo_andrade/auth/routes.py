from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user
from grupo_andrade.models import User
from grupo_andrade.atividade.services import registrar_atividade
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
import os


auth = Blueprint('auth', __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    google_auth_url = get_google_auth_url()
    return render_template('auth/login.html', google_auth_url=google_auth_url)

@auth.route('/login/callback')
def login_callback():
    code = request.args.get('code')
    
    if not code:
        flash('Falha na autenticação')
        return redirect(url_for('auth.login'))
    
    try:
        # Troca o código por um token
        token_response = exchange_code_for_token(code)
        
        # Valida o token e obtém informações do usuário
        user_info = validate_google_token(token_response['id_token'])
        # Obtém ou cria o usuário no banco de dados
        user = User.get_or_create(
            google_id=user_info['sub'],
            name=user_info['name'],
            email=user_info['email'],
            profile_pic=user_info.get('picture')
            
        )

        registrar_atividade(
            user.id,
            'LOGIN',
            f'Usuario {user.username.upper()} logado'
        )
        # Faz login do usuário
        login_user(user)
        
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('placas.homepage'))
        
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        flash('Erro na autenticação')
        return redirect(url_for('auth.login'))

# funcoes auxiliares 
def get_google_auth_url():
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    params = {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI'),
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    import urllib.parse
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(code):
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI')
    }
    
    response = requests.post(token_url, data=data)
    return response.json()

def validate_google_token(id_token_str):
    idinfo = id_token.verify_oauth2_token(
        id_token_str,
        google_requests.Request(),
        os.environ.get('GOOGLE_CLIENT_ID')
    )
    
    return idinfo


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()
    flash(f'Voce esta desconectado', category='warning')
    return redirect(url_for('auth.login'))
