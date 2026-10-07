from flask import Blueprint, request, jsonify
from db import query_all, query_one, pontuar, limite_arg, apelido_valido

flashcards_bp = Blueprint("flashcards", __name__)


@flashcards_bp.get("/")
def listar():
    """GET /flashcards/?tema=morfologia&limite=10"""
    sql, params = "SELECT id, tema, frente, verso FROM flashcards", []
    tema = request.args.get("tema")
    if tema:
        sql += " WHERE tema = %s"
        params.append(tema)
    sql += " ORDER BY RANDOM() LIMIT %s"
    params.append(limite_arg(request))
    return jsonify(query_all(sql, params))


@flashcards_bp.post("/<int:fid>/revisar")
def revisar(fid):
    """POST body: {"apelido": "ana", "sabia": true}"""
    dados = request.get_json(silent=True) or {}
    apelido = (dados.get("apelido") or "").strip()
    sabia = dados.get("sabia")

    if not apelido_valido(apelido) or not isinstance(sabia, bool):
        return jsonify({"erro": "Envie 'apelido' e 'sabia' (booleano)."}), 400

    if not query_one("SELECT 1 FROM flashcards WHERE id = %s", (fid,)):
        return jsonify({"erro": "Flashcard não encontrado."}), 404

    total = pontuar(apelido, sabia, 5)
    return jsonify({"sabia": sabia, "pontos_totais": total})
