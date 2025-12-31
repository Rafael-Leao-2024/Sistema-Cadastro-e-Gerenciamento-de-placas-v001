import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

APIKEY_SENDGRID = os.environ.get("APIKEY_SENDGRID")

def enviar_email_reset_senha(user, link_reset):
    try:
        import os
        import certifi
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['SSL_CERT_FILE'] = certifi.where()
        
        import sendgrid
        from sendgrid.helpers.mail import Mail
        
        sg = sendgrid.SendGridAPIClient(api_key=APIKEY_SENDGRID)
        
        html_content = f"""
        <p>Para redefinir sua senha, clique no link abaixo:<br><br>
        <a href="{link_reset}">{link_reset}</a></p>
        """
        
        message = Mail(
            from_email=os.getenv("MAIL_DEFAULT_SENDER"),
            to_emails=[user.email],
            subject="Solicitação de redefinição de senha",
            html_content=html_content
        )
        
        response = sg.send(message)
        print(f"E-mail enviado via SendGrid: {response.status_code}")
        return True
        
    except Exception as erro:
        print(f"Erro: {erro}")
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