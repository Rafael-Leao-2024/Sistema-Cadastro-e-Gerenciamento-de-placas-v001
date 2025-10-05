from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed
from wtforms.widgets import TextArea


class EmplacamentoForm(FlaskForm):
    placa = StringField('Placa', 
                       validators=[DataRequired(), Length(min=7, max=7)])
    renavan = StringField('Renavan', 
                         validators=[DataRequired(), Length(min=9, max=11)])
    endereco_placa = StringField('Endereco da Placa', 
                                validators=[DataRequired(), Length(min=5, max=100)],
                                widget=TextArea())
    crlv = StringField('CRLV', 
                      validators=[Optional(), Length(max=20)])
    submit = SubmitField('Solicitar')

class ConsultarForm(FlaskForm):
    chassi = StringField('Chassi', 
                       validators=[DataRequired(), Length(min=7, max=7)])
    submit = SubmitField('Consultar')

class PlacaStatusForm(FlaskForm):
    placa_confeccionada = BooleanField('Placa Confeccionada')
    placa_a_caminho = BooleanField('Placa a Caminho')
    submit = SubmitField('Atualizar Status')
    


class EmplacamentoUpdateForm(FlaskForm):
    placa = StringField('Placa', 
                       validators=[DataRequired(), Length(min=7, max=7)])
    renavan = StringField('Renavan', 
                         validators=[DataRequired(), Length(min=9, max=11)])
    endereco_placa = StringField('Endereco da Placa', 
                                validators=[DataRequired(), Length(min=5, max=100)],
                                )
    crlv = StringField('CRLV', 
                      validators=[Optional(), Length(max=20)])
    submit = SubmitField('Editar')