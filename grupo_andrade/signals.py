# app/signals.py
from flask_login import user_logged_out
from grupo_andrade.atividade.services import registrar_atividade

def register_signals(app):

    @user_logged_out.connect_via(app)
    def when_user_logged_out(sender, user):
        if user:
            registrar_atividade(
                usuario_id=user.id,
                acao="LOGOUT",
                descricao=f"{user.username.upper()} Encerramento de sessão"
            )
            
