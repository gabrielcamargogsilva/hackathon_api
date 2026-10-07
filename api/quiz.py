from flask import Blueprint, request, jsonify
from db import query_all, query_one, pontuar, limite_arg, apelido_valido

quiz_bp = Blueprint("quiz", __name__)
PONTOS = {"facil": 10, "medio": 20, "dificil": 30}


@quiz_bp.get("/")
def listar():
    """GET /quiz/?tema=sintaxe&nivel=facil&limite=10  (não envia o gabarito)"""
    sql, params = "SELECT * FROM questoes WHERE TRUE", []
    tema = request.args.get("tema")
    nivel = request.args.get("nivel")
    if tema:
        sql += " AND tema = %s"
        params.append(tema)
    if nivel:
        sql += " AND nivel = %s"
        params.append(nivel)
    sql += " ORDER BY RANDOM() LIMIT %s"
    params.append(limite_arg(request))

    return jsonify([
        {
            "id": q["id"],
            "tema": q["tema"],
            "nivel": q["nivel"],
            "pergunta": q["pergunta"],
            "alternativas": {"A": q["alt_a"], "B": q["alt_b"],
                             "C": q["alt_c"], "D": q["alt_d"]},
        }
        for q in query_all(sql, params)
    ])


@quiz_bp.post("/<int:qid>/responder")
def responder(qid):
    """POST body: {"apelido": "ana", "resposta": "B"}"""
    dados = request.get_json(silent=True) or {}
    apelido = (dados.get("apelido") or "").strip()
    escolha = (dados.get("resposta") or "").strip().upper()

    if not apelido_valido(apelido) or escolha not in ("A", "B", "C", "D"):
        return jsonify({"erro": "Envie 'apelido' (até 30 caracteres) e 'resposta' (A-D)."}), 400

    q = query_one("SELECT * FROM questoes WHERE id = %s", (qid,))
    if not q:
        return jsonify({"erro": "Questão não encontrada."}), 404

    correta = escolha == q["resposta"]
    total = pontuar(apelido, correta, PONTOS.get(q["nivel"], 10))
    return jsonify({
        "correta": correta,
        "resposta_certa": q["resposta"],
        "explicacao": q["explicacao"],
        "pontos_totais": total,
    })
