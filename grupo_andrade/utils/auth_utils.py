from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from grupo_andrade.models import User
from datetime import datetime

def gerar_token_reset(user, expires_sec=1800):
    """Gera token para reset de senha"""
    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    return s.dumps({'user_id': user.id})

def verificar_token_reset(token):
    """Verifica se o token de reset é válido"""
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token)['user_id']
    except:
        return None
    return User.query.get(user_id)

def calcular_idade(data_nascimento):
    """Calcula idade a partir da data de nascimento"""
    hoje = datetime.now().date()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
