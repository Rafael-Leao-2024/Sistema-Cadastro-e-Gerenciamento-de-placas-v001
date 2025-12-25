from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class FormularioBoleto(FlaskForm):
    descricao = StringField(
        'Descrição da Taxa',
        validators=[
            DataRequired(message='A descrição é obrigatória'),
            Length(min=3, max=100, message='A descrição deve ter entre 3 e 100 caracteres')
        ],
        render_kw={
            "placeholder": "Ex: IPVA 2024, Licenciamento, Multa de Trânsito",
            "class": "form-control"
        }
    )
    
    valor = DecimalField(
        'Valor (R$)',
        validators=[
            DataRequired(message='O valor é obrigatório'),
            NumberRange(min=0.01, max=99999.99, message='O valor deve ser positivo')
        ],
        places=2,
        render_kw={
            "placeholder": " ",
            "class": "form-control",
            "step": "0.01"
        }
    )
    
    submit = SubmitField(
        'Criar Boleto',
        render_kw={"class": "btn btn-primary"}
    )