import mercadopago
import os
from grupo_andrade.models import Pagamento
from dotenv import load_dotenv
import requests

load_dotenv()

def criar_pagamento_mercadopago(valor, descricao, usuario_id):
    """Cria preferência de pagamento no Mercado Pago"""
    sdk = mercadopago.SDK(os.getenv('PROD_ACCESS_TOKEN'))
    
    preference_data = {
        "items": [
            {
                "id": usuario_id,
                "title": descricao,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(valor),
            }
        ],
        "auto_return": "all",
    }
    
    return sdk.preference().create(preference_data)

# def verificar_status_pagamento(payment_id):
#     """Verifica status de um pagamento no Mercado Pago"""
#     sdk = mercadopago.SDK(os.getenv('PROD_ACCESS_TOKEN'))
#     payment = sdk.payment().get(payment_id)
    
#     if payment["status"] == 200:
#         return (
#             payment["response"]["transaction_amount"],
#             payment["response"]["id"],
#             payment["response"]["status"]
#         )
#     return None, None, None


def verificar_status_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    PROD_ACCESS_TOKEN = os.environ.get('PROD_ACCESS_TOKEN')
    headers = {
        "Authorization": f"Bearer {PROD_ACCESS_TOKEN}" 
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    valor_pago = None

    if response.status_code == 200 and response.json().get('status') == 'approved':
        payment_info = response.json()  # Converte a resposta para JSON
        status_pagamento = payment_info['status']
        id_pagamento = payment_info['point_of_interaction']['transaction_data']['transaction_id']
        valor_pago = payment_info.get('transaction_amount')
    else:
        payment_info = response.json() 
        status_pagamento = payment_info.get('status')
        id_pagamento = payment_id
    return valor_pago, id_pagamento, status_pagamento