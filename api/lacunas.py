from flask import Blueprint, request, jsonify
from db import query_all, query_one, pontuar, limite_arg, apelido_valido

lacunas_bp = Blueprint("lacunas", __name__)


@lacunas_bp.get("/")
def listar():
    """GET /lacunas/?tema=sintaxe&limite=5  (não envia o gabarito)"""
    sql, params = "SELECT id, tema, frase, opcoes FROM lacunas", []
    tema = request.args.get("tema")
    if tema:
        sql += " WHERE tema = %s"
        params.append(tema)
    sql += " ORDER BY RANDOM() LIMIT %s"
    params.append(limite_arg(request, padrao=5))
    return jsonify(query_all(sql, params))  # 'opcoes' (JSONB) já vira lista


@lacunas_bp.post("/<int:lid>/responder")
def responder(lid):
    """POST body: {"apelido": "ana", "resposta": "a"}"""
    dados = request.get_json(silent=True) or {}
    apelido = (dados.get("apelido") or "").strip()
    escolha = (dados.get("resposta") or "").strip()

    if not apelido_valido(apelido) or not escolha:
        return jsonify({"erro": "Envie 'apelido' e 'resposta'."}), 400

    r = query_one("SELECT * FROM lacunas WHERE id = %s", (lid,))
    if not r:
        return jsonify({"erro": "Lacuna não encontrada."}), 404

    correta = escolha.lower() == r["resposta"].lower()
    total = pontuar(apelido, correta, 15)
    return jsonify({
        "correta": correta,
        "resposta_certa": r["resposta"],
        "explicacao": r["explicacao"],
        "pontos_totais": total,
    })
