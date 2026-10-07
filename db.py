import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g, current_app



def get_conn():
    """Uma conexão por requisição, reaproveitada dentro dela."""
    if "db" not in g:
        url = current_app.config.get("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL não configurada (veja .env.example).")
        g.db = psycopg2.connect(url, cursor_factory=RealDictCursor)
    return g.db


def close_db(_e=None):
    _ = _e
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()  # transação não commitada sofre rollback


def query_all(sql, params=()):
    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def query_one(sql, params=()):
    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def init_db():
    """Cria as tabelas (idempotente)."""
    caminho = os.path.join(current_app.root_path, "schema.sql")
    with open(caminho, encoding="utf-8") as f:
        sql = f.read()
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def pontuar(apelido, acertou, pontos):
    """Cria o jogador se não existir e atualiza o placar em uma única query.
    Retorna o total de pontos atual."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO jogadores (apelido, pontos, acertos, erros)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (apelido) DO UPDATE SET
                pontos  = jogadores.pontos  + EXCLUDED.pontos,
                acertos = jogadores.acertos + EXCLUDED.acertos,
                erros   = jogadores.erros   + EXCLUDED.erros
            RETURNING pontos
            """,
            (apelido, pontos if acertou else 0, 1 if acertou else 0, 0 if acertou else 1),
        )
        total = cur.fetchone()["pontos"]
    conn.commit()
    return total


def limite_arg(request, padrao=10, maximo=30):
    try:
        return max(1, min(int(request.args.get("limite", padrao)), maximo))
    except ValueError:
        return padrao


def apelido_valido(apelido):
    return bool(apelido) and len(apelido) <= 30
