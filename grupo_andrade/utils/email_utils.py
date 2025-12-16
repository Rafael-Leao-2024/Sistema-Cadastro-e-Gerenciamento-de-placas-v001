from flask import  url_for
import requests
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

APIKEY_SENDGRID = os.environ.get("APIKEY_SENDGRID")  # Substitua pela sua chave


# Construa o e-mail
def enviar_email_reset_senha(user):
    token = user.get_reset_token()
    conta_sendgrid = SendGridAPIClient(os.environ.get('APIKEY_SENDGRID', APIKEY_SENDGRID))


    message = Mail(
        from_email=os.environ.get("EMAIL_SENDGRID"),  # Use um e-mail verificado
        to_emails=user.email,
        subject="Solicitação de redefinição de senha",
        html_content=f"""<p>
Para redefinir sua senha, visite o seguinte link:<br><br>
<a href="{url_for('auth.reset_token', token=token, _external=True)}">
{url_for('auth.reset_token', token=token, _external=True)}
</a><br><br>
Se você não fez esta solicitação, simplesmente ignore este e-mail e nenhuma alteração será feita.<br><br>
Obrigado,<br>
{user.username}</p>"""
)

    # Envie o e-mail
    try:
        resposta = conta_sendgrid.send(message=message)
        print(f"E-mail enviado! Status: {resposta.status_code}")
        return resposta.status_code
        # Status 202 indica sucesso:cite[3]
    except Exception as erro:
        print(f"Erro ao enviar e-mail: {erro}")
        return None


def verificar_email(email):
    CHAVE_API_DE_EMAIL = os.environ.get('CHAVE_API_DE_EMAIL')
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={CHAVE_API_DE_EMAIL}"    
    response = requests.get(url)
    dados = response.json()
    return dados.get('data', {}).get('status') == 'valid' or dados.get('data', {}).get('status') == 'accept_all'


def enviar_email_confirmacao_servivos(usuario, servicos):
    conta_sendgrid = SendGridAPIClient(APIKEY_SENDGRID)

    conteudo = ""
    for servico in servicos:
        conteudo += f"""<p>Placa {servico.placa}</p><p>Chassi {servico.chassi}</p></br>"""

    email = Mail(
        from_email=os.environ.get('MAIL_USERNAME'),
        to_emails=usuario.email,
        subject="Solicitaçoes de Serviço em demanda",
        html_content=conteudo
    )

    
    # Envie o e-mail
    try:
        resposta = conta_sendgrid.send(email)
        print(f"E-mail enviado! Status: {resposta.status_code}")
        # Status 202 indica sucesso:cite[3]
    except Exception as erro:
        print(f"Erro ao enviar e-mail: {erro}")