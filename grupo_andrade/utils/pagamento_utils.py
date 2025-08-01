from dotenv import load_dotenv
import requests
import json
import os


load_dotenv()

PROD_ACCESS_TOKEN = os.environ.get('PROD_ACCESS_TOKEN')

def criar_preferencia(placas):
    corpo = {"items":[{"id": str(placa.id), "title": placa.placa.upper(), "quantity": 1, "unit_price": 0.01}
                      for placa in placas],
            "back_urls": {
            "success": f"https://sistemacbm.com/#/login",
            "failure": f"https://sistemacbm.com/#/login",
            "pending": f"https://sistemacbm.com/#/login",
        },}
    corpo_js = json.dumps(corpo)
    headers = {"Authorization": f"Bearer {PROD_ACCESS_TOKEN}"}
    resposta = requests.post('https://api.mercadopago.com/checkout/preferences',
                             headers=headers, data=corpo_js)
    if resposta.status_code == 201:
        init_point = resposta.json()['init_point']
        total = sum(item['unit_price'] for item in resposta.json()['items'])
        return total, init_point
    return


def verificar_status_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {
        "Authorization": f"Bearer {PROD_ACCESS_TOKEN}"
    }
    response = requests.get(url=url, headers=headers)
    print(response.json())
    if response.status_code == 200 and response.json().get('status') == 'approved':
        payment_info = response.json()  # Converte a resposta para JSON
        status_pagamento = payment_info['status']
        id_pagamento = payment_info['point_of_interaction']['transaction_data']['transaction_id']
        valor_pago = payment_info.get('transaction_amount')
    else:
        payment_info = response.json()
        status_pagamento = payment_info.get('status')
        id_pagamento = payment_id
        valor_pago = payment_info.get('transaction_amount')

    return valor_pago, id_pagamento, status_pagamento