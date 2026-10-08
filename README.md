# API de Língua Portuguesa (Hackathon, ODS 4)

API REST para atividades de língua portuguesa. Implementada com Flask, Blueprints e PostgreSQL. Não há autenticação: o jogador é identificado pelo apelido enviado nas respostas.

**Autor do desenvolvimento back-end:** Gabriel Camargo Gonçalves Silva

## Executar localmente

Requer Python e PostgreSQL.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure `DATABASE_URL` no `.env` e carregue o conteúdo inicial:

```powershell
python seed.py
python -m flask --app app run
```

O `seed.py` cria as tabelas e carrega questões, flashcards e lacunas; ele limpa e recria esse conteúdo quando executado novamente, mas preserva os jogadores. Por padrão, a API fica disponível em `http://127.0.0.1:5000`.

## Contrato para o front-end

Consulte o [contrato de uso da API](docs/contrato-api.md) para integração: base URL, rotas, parâmetros, corpos JSON, respostas, erros e exemplos de chamadas.

## Convenções

- Base local: `http://127.0.0.1:5000`. Substitua-a pela URL do ambiente publicado no front-end.
- As respostas e os corpos JSON usam UTF-8. Em requisições POST, envie `Content-Type: application/json`.
- A API permite chamadas cross-origin (CORS).
- Atividades são selecionadas aleatoriamente; não dependa da ordem dos itens nem de IDs fixos entre ambientes.
- Temas disponíveis no conteúdo inicial: `sintaxe`, `morfologia`, `pragmatica`, `revisao_geral`.
- Níveis do quiz: `facil`, `medio`, `dificil`.
- `limite` é limitado ao intervalo de 1 a 30. Se for omitido, inválido ou não numérico, usa o padrão indicado abaixo.
- Apelidos são removidos de espaços nas pontas e devem ter de 1 a 30 caracteres.
- Cada resposta/revisão atualiza o total de `acertos` ou `erros` do jogador; apenas os pontos concedidos mudam conforme a atividade e o resultado.
- Os endpoints de listagem não exigem corpo. Os endpoints de resposta/revisão exigem JSON conforme os exemplos.

## Rotas

| Método | Caminho | Parâmetros | Corpo |
|---|---|---|---|
| GET | `/` | — | — |
| GET | `/quiz/` | `tema`, `nivel`, `limite` (padrão 10) | — |
| POST | `/quiz/<id>/responder` | — | `{"apelido": "ana", "resposta": "B"}` |
| GET | `/flashcards/` | `tema`, `limite` (padrão 10) | — |
| POST | `/flashcards/<id>/revisar` | — | `{"apelido": "ana", "sabia": true}` |
| GET | `/lacunas/` | `tema`, `limite` (padrão 5) | — |
| POST | `/lacunas/<id>/responder` | — | `{"apelido": "ana", "resposta": "a"}` |
| GET | `/ranking` | — | — |
| GET | `/jogadores/<apelido>` | apelido no caminho | — |

Os caminhos de listagem terminam em `/`. Os parâmetros de consulta são opcionais, por exemplo: `/quiz/?tema=sintaxe&nivel=facil&limite=5`.

## Contratos por rota

### `GET /`

Verifica se a API está ativa.

```json
{"status": "API on"}
```

### `GET /quiz/`

Retorna questões sem o gabarito. Cada questão contém `id`, `tema`, `nivel`, `pergunta` e as alternativas identificadas por `A` a `D`.

Exemplo: `GET /quiz/?tema=sintaxe&nivel=facil&limite=1`

```json
[
  {
    "id": 1,
    "tema": "sintaxe",
    "nivel": "facil",
    "pergunta": "Qual é o sujeito em 'Os alunos chegaram cedo à escola'?",
    "alternativas": {
      "A": "Os alunos",
      "B": "cedo",
      "C": "à escola",
      "D": "chegaram"
    }
  }
]
```

### `POST /quiz/<id>/responder`

Envie uma das letras `A`, `B`, `C` ou `D` (maiúsculas ou minúsculas). Questões fáceis valem 10 pontos, médias 20 e difíceis 30; uma resposta incorreta não soma pontos.

```json
{
  "apelido": "ana",
  "resposta": "B"
}
```

Resposta de sucesso (`200`):

```json
{
  "correta": true,
  "resposta_certa": "B",
  "explicacao": "Explicação da resposta correta.",
  "pontos_totais": 20
}
```

### `GET /flashcards/`

Retorna `id`, `tema`, `frente` e `verso`. A API entrega os dois lados; o front-end pode mostrar `frente` primeiro e revelar `verso` após a interação do usuário.

Exemplo: `GET /flashcards/?tema=morfologia&limite=1`

```json
[
  {
    "id": 1,
    "tema": "morfologia",
    "frente": "O que é radical?",
    "verso": "Parte da palavra que carrega o significado básico."
  }
]
```

### `POST /flashcards/<id>/revisar`

`sabia` deve ser um booleano JSON (`true` ou `false`, não texto). Uma revisão marcada como conhecida vale 5 pontos; marcada como não conhecida não soma pontos.

```json
{
  "apelido": "ana",
  "sabia": true
}
```

Resposta de sucesso (`200`):

```json
{
  "sabia": true,
  "pontos_totais": 5
}
```

### `GET /lacunas/`

Retorna `id`, `tema`, `frase` e `opcoes`, sem enviar a resposta correta.

Exemplo: `GET /lacunas/?tema=sintaxe&limite=1`

```json
[
  {
    "id": 1,
    "tema": "sintaxe",
    "frase": "Ele chegou ___ casa cedo.",
    "opcoes": ["em", "a", "na"]
  }
]
```

### `POST /lacunas/<id>/responder`

Envie em `resposta` uma das opções recebidas. A comparação não diferencia maiúsculas e minúsculas. Uma resposta correta vale 15 pontos; uma incorreta não soma pontos.

```json
{
  "apelido": "ana",
  "resposta": "a"
}
```

Resposta de sucesso (`200`):

```json
{
  "correta": true,
  "resposta_certa": "a",
  "explicacao": "Explicação da resposta correta.",
  "pontos_totais": 15
}
```

### `GET /ranking`

Retorna até 10 jogadores, ordenados por pontos decrescentes e, em caso de empate, por apelido.

```json
[
  {"apelido": "ana", "pontos": 120},
  {"apelido": "bia", "pontos": 95}
]
```

### `GET /jogadores/<apelido>`

Retorna o placar do jogador. Para um apelido ainda não registrado, retorna os valores iniciais sem criar o jogador.

```json
{
  "apelido": "ana",
  "pontos": 120,
  "acertos": 8,
  "erros": 3
}
```

## Erros e validação

Os erros de validação e de recurso inexistente são JSON:

```json
{"erro": "Envie 'apelido' (até 30 caracteres) e 'resposta' (A-D)."}
```

| Código HTTP | Quando |
|---|---|
| `200` | Consulta ou resposta processada com sucesso |
| `400` | Corpo ausente/malformado ou campos inválidos |
| `404` | ID de questão, flashcard ou lacuna inexistente |
| `500` | Erro interno; corpo genérico `{"erro": "Erro interno do servidor."}` |

Mensagens `400` e `404` variam conforme a rota. Perfil inexistente é exceção: retorna `200` com pontos, acertos e erros iguais a zero.

## Integração rápida no front-end

Exemplo de chamada do quiz usando `fetch`:

```javascript
const API_BASE_URL = "http://127.0.0.1:5000";

const questoes = await fetch(
  `${API_BASE_URL}/quiz/?tema=sintaxe&nivel=facil&limite=5`
).then(async (response) => {
  if (!response.ok) throw new Error(`Falha ao carregar quiz: ${response.status}`);
  return response.json();
});

const questao = questoes[0];
// Renderize questao.pergunta e questao.alternativas.A, .B, .C e .D.

const resultado = await fetch(`${API_BASE_URL}/quiz/${questao.id}/responder`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ apelido: "ana", resposta: "B" }),
}).then(async (response) => {
  const data = await response.json();
  if (!response.ok) throw new Error(data.erro ?? "Falha ao enviar resposta");
  return data;
});
// resultado.correta, resultado.resposta_certa, resultado.explicacao,
// resultado.pontos_totais
```

Para integrar as outras atividades, use os campos e corpos indicados em seus contratos. Mantenha o `id` retornado na listagem para enviar a resposta ou a revisão ao endpoint correspondente.

## Testes de rotas

Os testes automatizados exercitam as nove operações HTTP pelo cliente de teste do Flask. As consultas e atualizações ao banco são simuladas para que os testes não alterem o PostgreSQL.

```powershell
python -m unittest -v test_api.py
```
