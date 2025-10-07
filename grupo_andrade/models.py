from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from .main import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(100), nullable=False)
    placas = db.relationship('Placa', backref='author', lazy=True, cascade='all, delete-orphan')
    enderecos = db.relationship('Endereco', backref='user', lazy=True, cascade='all, delete-orphan')
    pagamentos = db.relationship('Pagamento', backref='user', lazy=True, cascade='all, delete-orphan')
    is_admin = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime)
    despachante = db.Column(db.Integer, default=None)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id, 'exp': expires_sec})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User(username={self.username}, email={self.email}, admin={self.is_admin})"


class Placa(db.Model):
    __tablename__ = 'placas'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), nullable=False, default="ABC1234")
    chassi = db.Column(db.String(30), nullable=True, default=000000)
    renavan = db.Column(db.String(20))
    endereco_placa = db.Column(db.String(100), nullable=False)
    crlv = db.Column(db.String(20))
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    received = db.Column(db.Boolean, default=False)
    received_at = db.Column(db.DateTime)
    placa_confeccionada = db.Column(db.Boolean, default=False)
    placa_a_caminho = db.Column(db.Boolean, default=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_user_recebeu = db.Column(db.Integer)

    uploads = db.relationship('UploadFile', backref='placa', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Placa('{self.placa}', '{self.date_create}')"


class Endereco(db.Model):
    __tablename__ = 'enderecos'
    
    id = db.Column(db.Integer, primary_key=True)
    endereco = db.Column(db.String(200), nullable=False, default="Nenhum")
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Endereco('{self.endereco}')"


class Pagamento(db.Model):
    
    __tablename__ = 'pagamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pagamento = db.Column(db.String(100), nullable=False)
    status_pagamento = db.Column(db.String(50), nullable=False)
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    valor_transacao = db.Column(db.Float)

    def __repr__(self):
        return f"Pagamento(id={self.id_pagamento}, status={self.status_pagamento}, valor_transacao={self.valor_transacao})"


class UploadFile(db.Model):

    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), unique=False, nullable=False)
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_placa = db.Column(db.Integer, db.ForeignKey('placas.id'), nullable=False)
    
class Notificacao(db.Model):

    __tablename__ = 'notificacoes'

    id = db.Column(db.Integer, primary_key=True)
    mensagem = db.Column(db.String(200), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    id_solicitacao = db.Column(db.Integer, db.ForeignKey('placas.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    solicitacao = db.relationship('Placa', backref='notificacoes', lazy=True)

    def __repr__(self):
        return f"Notificacao(mensagem='{self.mensagem}', lida={self.lida})"