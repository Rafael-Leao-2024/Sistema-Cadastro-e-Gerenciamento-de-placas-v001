import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# URL pública do Railway
DATABASE_URL = os.environ.get('DATABASE_URL')
try:
    # Força UTF-8 no driver
    engine = create_engine(DATABASE_URL, connect_args={'client_encoding': 'utf8'})

    # Teste de conexão
    with engine.connect() as conn:
        print("✅ Conexão com o banco bem-sucedida!")

except Exception as e:
    # Mostra apenas a mensagem de erro de forma segura
    print("❌ Erro ao conectar ao banco:", repr(e))
