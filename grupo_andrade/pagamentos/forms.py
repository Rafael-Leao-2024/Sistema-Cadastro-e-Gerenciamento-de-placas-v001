from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

class RelatorioForm(FlaskForm):
    mes = SelectField('Mes', 
                     choices=[(i, f'{i:02d}') for i in range(1, 13)],
                     validators=[DataRequired()],
                     default=datetime.now().month)
    ano = SelectField('Ano', 
                     choices=[(i, i) for i in range(2020, datetime.now().year + 1)],
                     validators=[DataRequired()],
                     default=datetime.now().year)
    submit = SubmitField('Gerar Relatorio')