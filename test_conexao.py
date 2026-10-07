import os
import sys

try:
    from dotenv import load_dotenv
    import psycopg2
except ImportError as e:
    sys.exit(f"Falta instalar: {e}. Rode: pip install -r requirements.txt")

load_dotenv()
url = os.getenv("DATABASE_URL")

if not url:
    sys.exit("DATABASE_URL não foi lida. O .env está na mesma pasta deste arquivo? "
             "O nome é exatamente '.env' (e não '.env.txt')?")

# mostra a URL sem a senha, para conferir o resto
visivel = url.split("://")[0] + "://" + url.split("@")[-1]
print("Tentando conectar em:", visivel)

try:
    conn = psycopg2.connect(url, connect_timeout=10)
    print("Conectou! Versão do servidor:", conn.server_version)
    conn.close()
except Exception as e:
    print("FALHOU:", type(e).__name__)
    print(e)