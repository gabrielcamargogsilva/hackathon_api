from flask import Blueprint, jsonify
from db import query_all, query_one

jogadores_bp = Blueprint("jogadores", __name__)


@jogadores_bp.get("/ranking")
def ranking():
    return jsonify(query_all(
        "SELECT apelido, pontos FROM jogadores ORDER BY pontos DESC, apelido LIMIT 10"))


@jogadores_bp.get("/jogadores/<apelido>")
def perfil(apelido):
    r = query_one("SELECT * FROM jogadores WHERE apelido = %s", (apelido,))
    if not r:
        return jsonify({"apelido": apelido, "pontos": 0, "acertos": 0, "erros": 0})
    return jsonify(r)
