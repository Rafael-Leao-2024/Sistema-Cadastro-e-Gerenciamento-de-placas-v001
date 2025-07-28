from datetime import datetime
from grupo_andrade.models import Placa
from sqlalchemy import extract

def formatar_data_completa(data):
    """Formata data no padrão dd/mm/YYYY HH:MM"""
    return data.strftime('%d/%m/%Y %H:%M') if data else ""

def verificar_status_placa(placa):
    """Retorna o status atual da placa"""
    if placa.received:
        return "Recebida"
    elif placa.placa_a_caminho:
        return "A caminho"
    elif placa.placa_confeccionada:
        return "Confeccionada"
    return "Pendente"

def contar_placas_por_mes(user_id, mes, ano):
    """Conta placas de um usuário em determinado mês/ano"""
    return Placa.query.filter(
        Placa.id_user == user_id,
        extract('month', Placa.date_create) == mes,
        extract('year', Placa.date_create) == ano
    ).count()