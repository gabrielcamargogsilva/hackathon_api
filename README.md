# API de Língua Portuguesa (Hackathon, ODS 4)

Flask + Blueprints + PostgreSQL. Sem autenticação: o jogador é identificado por um apelido.

## Rodar

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # edite DATABASE_URL
python seed.py              # cria tabelas + conteúdo
flask --app app run
```

## Rotas

| Método | Rota | Corpo / Query |
|---|---|---|
| GET | `/quiz/` | `?tema=&nivel=&limite=` |
| POST | `/quiz/<id>/responder` | `{apelido, resposta: "A"-"D"}` |
| GET | `/flashcards/` | `?tema=&limite=` |
| POST | `/flashcards/<id>/revisar` | `{apelido, sabia: true/false}` |
| GET | `/lacunas/` | `?tema=&limite=` |
| POST | `/lacunas/<id>/responder` | `{apelido, resposta}` |
| GET | `/ranking` | Top 10 |
| GET | `/jogadores/<apelido>` | Pontos, acertos, erros |

Temas: `sintaxe`, `morfologia`, `pragmatica`, `revisao_geral`. Níveis: `facil`, `medio`, `dificil`.
