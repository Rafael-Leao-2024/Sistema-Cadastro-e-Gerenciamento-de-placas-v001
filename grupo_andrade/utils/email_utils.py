from flask import current_app
import os
import smtplib
from email.mime.text import MIMEText
from flask import url_for
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import threading

from dotenv import load_dotenv

load_dotenv()

APIKEY_SENDGRID = os.environ.get("APIKEY_SENDGRID")  # Substitua pela sua chave


def enviar_email_reset_senha(user, link_reset):
    try:
        remetente = os.getenv("MAIL_DEFAULT_SENDER")
        senha_app = os.getenv("MAIL_PASSWORD")

        html = f"""
        <p>
            Para redefinir sua senha, clique no link abaixo:<br><br>
            <a href="{link_reset}">{link_reset}</a><br><br>
            Se você não solicitou a redefinição, ignore este e-mail.<br><br>
            Atenciosamente,<br>
            <strong>{user.username}</strong>
        </p>
        """

        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = "Solicitação de redefinição de senha"
        msg["From"] = remetente
        msg["To"] = user.email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remetente, senha_app)
            server.send_message(msg)

        print("E-mail de redefinição enviado com sucesso")
        return True

    except Exception as erro:
        print(f"Erro ao enviar e-mail de redefinição: {erro}")
        return False


def enviar_email_em_background(user, link_reset):
    import threading
    from flask import current_app

    app = current_app._get_current_object()

    def task():
        with app.app_context():
            enviar_email_reset_senha(user, link_reset)

    threading.Thread(target=task).start()



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