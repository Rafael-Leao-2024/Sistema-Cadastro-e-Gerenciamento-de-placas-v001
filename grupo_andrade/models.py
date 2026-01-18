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
    username = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(400), nullable=False, default='padrao.png')
    is_admin = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    despachante = db.Column(db.Integer, default=0)

    cpf_cnpj = db.Column(db.String(100), nullable=False, default='00.000.000.0000/00 ou 000.000.000-00')
    rg = db.Column(db.String(100), nullable=False, default='71.69553 SDS-PE')

    placas = db.relationship('Placa', backref='author', lazy=True, cascade='all, delete-orphan')
    uploads = db.relationship('UploadFile', backref='author', lazy=True, cascade='all, delete-orphan')
    enderecos = db.relationship('Endereco', backref='user', lazy=True, cascade='all, delete-orphan')
    pagamentos = db.relationship('Pagamento', backref='user', lazy=True, cascade='all, delete-orphan')
    notificacoes = db.relationship('Notificacao', backref='user', lazy=True, cascade='all, delete-orphan')
    boletos = db.relationship('Boleto', backref='author', lazy=True, cascade='all, delete-orphan')
    atividades = db.relationship('Atividade', backref='author', lazy=True, cascade='all, delete-orphan')


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id, 'exp': expires_sec})
    
    @property
    def meu_despachante(self):
        despachante = User.query.filter(User.id == self.despachante).first()
        if not despachante:
            return "Ainda nao ha despachante"
        return despachante.username
    
    def calcular_honorarios(self):
        honorarios = [placa.honorario for placa in self.placas if placa.honorario]
        total = sum(honorarios)
        return total
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    @staticmethod
    def get_or_create(google_id, name, email, profile_pic):
        user = User.query.get(google_id[-4:])
        if not user:
            user = User(
                id=google_id[-4:],
                username=name,
                email=email,
                image_file=profile_pic,
            )
            db.session.add(user)
            db.session.commit()
        return user

    def __repr__(self):
        return f"User(username={self.username}, email={self.email}, admin={self.is_admin})"


class Placa(db.Model):
    __tablename__ = 'placas'
    
    id = db.Column(db.Integer, primary_key=True)

    placa = db.Column(db.String(10), nullable=False, default="ABC1234")
    chassi = db.Column(db.String(30), nullable=True, default=000000)
    renavan = db.Column(db.String(20))
    endereco_placa = db.Column(db.String(100), nullable=False, default="nenhum")
    crlv = db.Column(db.String(20))
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.now)
    received = db.Column(db.Boolean, default=False)
    received_at = db.Column(db.DateTime)
    placa_confeccionada = db.Column(db.Boolean, default=False)
    placa_a_caminho = db.Column(db.Boolean, default=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_user_recebeu = db.Column(db.Integer)

    honorario = db.Column(db.Float, nullable=False, default=1.01)
    nome_proprietario = db.Column(db.String(40), unique=False, nullable=True, default="vazio")

    uploads = db.relationship('UploadFile', backref='placa', lazy=True, cascade='all, delete-orphan')
    notificacoes = db.relationship('Notificacao', backref='placa', lazy=True, cascade='all, delete-orphan')
    boletos = db.relationship('Boleto', backref='placa', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Placa('{self.placa}', '{self.date_create}')"


class Endereco(db.Model):
    __tablename__ = 'enderecos'
    
    id = db.Column(db.Integer, primary_key=True)
    rua = db.Column(db.String(100), nullable=True, default="Nenhum")
    cep = db.Column(db.String(50), nullable=True, default="Nenhum")
    bairro = db.Column(db.String(100), nullable=True, default="Nenhum")
    cidade = db.Column(db.String(100), nullable=True, default="Nenhum")
    uf = db.Column(db.String(100), nullable=True, default="Nenhum")
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"Endereco('{self.endereco}')"


class Pagamento(db.Model):
    
    __tablename__ = 'pagamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pagamento = db.Column(db.String(100), nullable=False)
    status_pagamento = db.Column(db.String(50), nullable=False)
    data_pagamento = db.Column(db.DateTime, default=datetime.now)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    valor_transacao = db.Column(db.Float)

    def __repr__(self):
        return f"Pagamento(id={self.id_pagamento}, status={self.status_pagamento}, valor_transacao={self.valor_transacao})"


class UploadFile(db.Model):

    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), unique=False, nullable=False, default="vazio")
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.now)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_placa = db.Column(db.Integer, db.ForeignKey('placas.id'), nullable=False)


class Boleto(db.Model):
    __tablename__ = "boletos"

    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.now)
    id_placa = db.Column(db.Integer, db.ForeignKey("placas.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("users.id"), name='fk_boleto_usuario', nullable=False)
    taxas = db.relationship('Taxa', backref='boleto', lazy=True, cascade='all, delete-orphan')

    def total_taxas(self):
        return sum(taxa.valor for taxa in self.taxas if taxa.valor)
    
    def __repr__(self):
        return f"<Boleto {self.id}>"
    
    

class Taxa(db.Model):
    __tablename__ = "taxas"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(150), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    id_boleto = db.Column(db.Integer, db.ForeignKey("boletos.id"), nullable=False)

    def __repr__(self):
        return f"<Taxa {self.descricao} - {self.valor}>"


    
class Notificacao(db.Model):

    __tablename__ = 'notificacoes'

    id = db.Column(db.Integer, primary_key=True)
    mensagem = db.Column(db.String(200), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    id_solicitacao = db.Column(db.Integer, db.ForeignKey('placas.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    def __repr__(self):
        return f"Notificacao(mensagem='{self.mensagem}', lida={self.lida})"
    

class Atividade(db.Model):
    __tablename__ = "atividades"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), name='fk_atividade_user',nullable=False)
    acao = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    data = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Atividade {self.acao} - Usuario {self.usuario_id}>"