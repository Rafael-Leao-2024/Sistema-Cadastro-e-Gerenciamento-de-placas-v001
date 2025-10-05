import re
from wtforms.validators import ValidationError

def validar_placa(form, field):
    """Valida formato de placa (Mercosul ou antigo)"""
    placa = field.data.upper()
    padrao_antigo = re.compile(r'^[A-Z]{3}\d{4}$')
    padrao_mercosul = re.compile(r'^[A-Z]{3}\d[A-Z]\d{2}$')
    
    if not (padrao_antigo.match(placa) or padrao_mercosul.match(placa)):
        raise ValidationError('Formato de placa inválido. Use AAA1234 ou AAA1B23')

def validar_renavam(form, field):
    """Valida numero do RENAVAM"""
    renavam = field.data
    if len(renavam) not in (9, 11) or not renavam.isdigit():
        raise ValidationError('RENAVAM deve ter 9 ou 11 dígitos numericos')

def validar_email_dominio(form, field):
    """Valida se email nao e de dominio temporario"""
    dominios_bloqueados = ['mailinator.com', 'tempmail.com', '10minutemail.com']
    dominio = field.data.split('@')[-1]
    if dominio in dominios_bloqueados:
        raise ValidationError('Este dominio de email nao e permitido')
    