from flask_mail import Message
from flask import  url_for, current_app as app
from grupo_andrade.main import mail
import requests
import os
from dotenv import load_dotenv

load_dotenv()


import requests
import os

def enviar_email_reset_senha(user):
    token = user.get_reset_token()
    link = f"{url_for('auth.reset_token', token=token, _external=True)}"
    corpo = f"""
    Para redefinir sua senha, visite o seguinte link:
    {link}

    Se você não fez esta solicitação, ignore este e-mail.
    """

    headers = {
        "accept": "application/json",
        "api-key": os.getenv("CHAVE_API_DE_EMAIL_BRAVO"),
        "content-type": "application/json",
    }

    data = {
        "sender": {"name": "Grupo Andrade", "email": "rafaelampaz6@gmail.com"},
        "to": [{"email": user.email}],
        "subject": "Redefinição de Senha",
        "textContent": corpo,
    }

    response = requests.post("https://api.brevo.com/v3/smtp/email", headers=headers, json=data)
    if response.status_code != 201:
        print("Erro ao enviar e-mail:", response.text)


# def enviar_email_reset_senha(user):
#     with mail.connect() as conn:
#         token = user.get_reset_token()
#         mensagem = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email, app.config['MAIL_DEFAULT_SENDER']])
#         mensagem.body = f'''Para redefinir sua senha, visite o seguinte link::
# {url_for('auth.reset_token', token=token, _external=True)}
# Se voce nao fez esta solicitacao, simplesmente ignore este e-mail e nenhuma alteração será feita.
# obrigado {user.username}
# '''
#         conn.send(mensagem)


def enviar_email_confirmacao_placa(user, placas):
    mensagem = Message(
        subject='Solicitacao de Placas',
        recipients=[user.email]
    )
    detalhes_placas = ""
    for placa in placas:
        detalhes_placas += f'''
CHASSI:  {placa.chassi.upper()}
Placa:  {placa.placa.upper()}
RENAVAM:{placa.renavan}
CRLV:   {placa.crlv}
Endereço de entrega: {placa.endereco_placa.title()}
Link para detalhes: {url_for('placas.placa_detail', placa_id=placa.id, _external=True)}
'''
    mensagem.body = f'''
Olá Grupo Andrade,
Segue abaixo os detalhes das solicitacoes de placas:
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
