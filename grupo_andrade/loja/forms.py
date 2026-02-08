from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class LojaForm(FlaskForm):
    nome = StringField('Nome da Loja', 
                      validators=[
                          DataRequired(message='O nome da loja é obrigatório'),
                          Length(min=2, max=120, message='Nome deve ter entre 2 e 120 caracteres')
                      ])
    
    cnpj = StringField('CNPJ', 
                      validators=[
                          Optional(),
                          Length(min=14, max=18, message='CNPJ deve ter 14 dígitos')
                      ])
    
    ativa = BooleanField('Loja Ativa', default=True)
    
    submit = SubmitField('Criar Loja')
    
    