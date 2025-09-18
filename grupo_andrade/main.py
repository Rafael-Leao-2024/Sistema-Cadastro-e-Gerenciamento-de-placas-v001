from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

mail = Mail()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'documentos') 
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db=db)
    
    from grupo_andrade.auth.routes import auth
    from grupo_andrade.users.routes import users
    from grupo_andrade.admin.routes import admin
    from grupo_andrade.placas.routes import placas
    from grupo_andrade.pagamentos.routes import pagamentos
    from grupo_andrade.support.routes import support
    from grupo_andrade.upload.routes import documentos_bp
    from grupo_andrade.despachante.routes import despachante
    
    
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(placas)
    app.register_blueprint(pagamentos)
    app.register_blueprint(support)
    app.register_blueprint(documentos_bp)
    app.register_blueprint(despachante)
    
    return app