from flask_mail import Message
from flask import  url_for
from grupo_andrade.main import mail
import requests
import os


def enviar_email_reset_senha(user):
    token = user.get_reset_token()
    mensagem = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    mensagem.body = f'''Para redefinir sua senha, visite o seguinte link::
{url_for('auth.reset_token', token=token, _external=True)}
Se você não fez esta solicitação, simplesmente ignore este e-mail e nenhuma alteração será feita.
obrigado {user.username}
'''
    mail.send(mensagem)


def enviar_email_confirmacao_placa(user, placas):
    mensagem = Message(
        subject='Solicitação de Placas',
        recipients=[user.email]
    )
    detalhes_placas = ""
    for placa in placas:
        detalhes_placas += f'''
Placa:  {placa.placa.upper()}
RENAVAM:{placa.renavan}
CRLV:   {placa.crlv}
Endereço de entrega: {placa.endereco_placa.title()}
Link para detalhes: {url_for('placas.placa_detail', placa_id=placa.id, _external=True)}
'''
    mensagem.body = f'''
Olá Grupo Andrade,
Segue abaixo os detalhes das solicitações de placas:
{detalhes_placas}

Atenciosamente,
{user.username}
Equipe de Atendimento
'''
    mail.send(mensagem)


def verificar_email(email):
    CHAVE_API_DE_EMAIL = os.environ.get('CHAVE_API_DE_EMAIL')
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={CHAVE_API_DE_EMAIL}"    
    response = requests.get(url)
    dados = response.json()
    return dados.get('data', {}).get('status') == 'valid' or dados.get('data', {}).get('status') == 'accept_all'