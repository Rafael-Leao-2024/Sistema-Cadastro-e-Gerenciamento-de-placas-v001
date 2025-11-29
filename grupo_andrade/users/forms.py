from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_wtf.file import FileField, FileAllowed
from grupo_andrade.models import User
from flask_login import current_user

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    rg = StringField('rg', 
                          validators=[DataRequired(), Length(min=2, max=20)])
    
    cpf_cnpj = StringField('cpf_cnpj', 
                          validators=[DataRequired(), Length(min=2, max=20)])


    picture = FileField('Update Profile Picture', 
                        validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Esse username ja esta em uso. Por favor escolha outro.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Esse email ja esta em uso. Por favor escolha outro.')

class EnderecoForm(FlaskForm):
    rua = StringField('Rua',
                          validators=[DataRequired(), Length(min=2, max=200)],
                          )
    
    bairro = StringField('bairro',
                          validators=[DataRequired(), Length(min=2, max=200)],
                          )
    
    cep = StringField('cep',
                          validators=[DataRequired(), Length(min=5, max=20)],
                          )
    
    cidade = StringField('cidade',
                          validators=[DataRequired(), Length(min=2, max=200)],
                          )
    
    uf = StringField('uf',
                          validators=[DataRequired(), Length(min=2, max=20)],
                          )



    submit = SubmitField('Atualizar Endereço')