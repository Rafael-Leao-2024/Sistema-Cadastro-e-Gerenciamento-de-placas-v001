from flask_mail import Message
from flask import  url_for, current_app as app
from grupo_andrade.main import mail
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def enviar_email_reset_senha(user):
    token = user.get_reset_token()
    mensagem = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email, app.config['MAIL_DEFAULT_SENDER']])
    mensagem.body = f'''Para redefinir sua senha, visite o seguinte link::
{url_for('auth.reset_token', token=token, _external=True)}
Se voce nao fez esta solicitacao, simplesmente ignore este e-mail e nenhuma alteração será feita.
obrigado {user.username}
'''
    mail.send(mensagem)


# def enviar_email_confirmacao_placa(user, placas):
#     mensagem = Message(
#         subject='Solicitacao de Placas',
#         recipients=[user.email]
#     )
#     detalhes_placas = ""
#     for placa in placas:
#         detalhes_placas += f'''
# CHASSI:  {placa.chassi.upper()}
# Placa:  {placa.placa.upper()}
# RENAVAM:{placa.renavan}
# CRLV:   {placa.crlv}
# Endereço de entrega: {placa.endereco_placa.title()}
# Link para detalhes: {url_for('placas.placa_detail', placa_id=placa.id, _external=True)}
# '''
#     mensagem.body = f'''
# Olá Grupo Andrade,
# Segue abaixo os detalhes das solicitacoes de placas:
# {detalhes_placas}

# Atenciosamente,
# {user.username}
# Equipe de Atendimento
# '''
#     with mail.connect() as conn:
#         conn.send(mensagem)


def verificar_email(email):
    CHAVE_API_DE_EMAIL = os.environ.get('CHAVE_API_DE_EMAIL')
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={CHAVE_API_DE_EMAIL}"    
    response = requests.get(url)
    dados = response.json()
    return dados.get('data', {}).get('status') == 'valid' or dados.get('data', {}).get('status') == 'accept_all'


from threading import Thread
from flask import current_app

def enviar_email_confirmacao_placa_async(app, user, placas):
    """Função para enviar email em background"""
    with app.app_context():
        # Seu código original de email aqui
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
        try:
            mail.send(mensagem)
            print("Email enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")

def enviar_email_confirmacao_placa(user, placas):
    """Função principal que chama o email em thread"""
    app = current_app._get_current_object()
    thread = Thread(target=enviar_email_confirmacao_placa_async, args=(app, user, placas))
    thread.start()
    return thread