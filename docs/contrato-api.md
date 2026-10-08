# Contrato de uso da API — Front-end

Este documento define como o front-end deve consumir a API de Língua Portuguesa. Os exemplos de payload são JSON e refletem os campos entregues e recebidos atualmente pela API.

## 1. Configuração e convenções

- **URL local:** `http://127.0.0.1:5000`
- Configure a URL da API por ambiente (desenvolvimento, homologação e produção); não fixe a URL local na versão publicada.
- A API habilita CORS.
- Requisições POST devem enviar `Content-Type: application/json` e corpo JSON.
- Respostas JSON usam nomes de campos em português.
- Não há autenticação. O jogador é identificado pelo campo `apelido`.
- Os endpoints de listagem retornam itens em ordem aleatória. Use sempre o `id` recebido para responder/revisar e não dependa de IDs ou de uma ordem fixa entre ambientes.
- Os filtros `tema` e `nivel` são opcionais. Os valores listados neste documento correspondem ao conteúdo inicial; a API não rejeita filtros desconhecidos, mas provavelmente retornará uma lista vazia.

### Valores do conteúdo inicial

Temas: `sintaxe`, `morfologia`, `pragmatica`, `revisao_geral`.

Níveis do quiz: `facil`, `medio`, `dificil`.

`limite` controla a quantidade solicitada e é limitado pela API ao intervalo de 1 a 30. Se omitido ou não numérico, aplica-se o padrão da rota: quiz e flashcards `10`, lacunas `5`. Valores abaixo de 1 tornam-se `1`; acima de 30 tornam-se `30`.

## 2. Resumo das rotas

| Método | Caminho | Uso |
|---|---|---|
| `GET` | `/` | Verificar disponibilidade da API |
| `GET` | `/quiz/` | Listar questões |
| `POST` | `/quiz/{id}/responder` | Enviar alternativa da questão |
| `GET` | `/flashcards/` | Listar flashcards |
| `POST` | `/flashcards/{id}/revisar` | Registrar se o jogador sabia o conteúdo |
| `GET` | `/lacunas/` | Listar exercícios de completar lacunas |
| `POST` | `/lacunas/{id}/responder` | Enviar resposta para uma lacuna |
| `GET` | `/ranking` | Obter os 10 primeiros jogadores |
| `GET` | `/jogadores/{apelido}` | Obter pontuação e estatísticas do jogador |

Os caminhos das três listagens incluem a barra final (`/quiz/`, `/flashcards/`, `/lacunas/`). Os caminhos de resposta, ranking e perfil não incluem barra final.

## 3. Contratos por funcionalidade

### 3.1 Disponibilidade

`GET /`

Resposta `200`:

```json
{
  "status": "API on"
}
```

### 3.2 Quiz

#### Buscar questões

`GET /quiz/?tema=sintaxe&nivel=facil&limite=5`

Todos os parâmetros de consulta são opcionais:

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `tema` | string | Filtra pelo tema |
| `nivel` | string | Filtra pelo nível |
| `limite` | inteiro | Quantidade desejada; padrão `10`, máximo `30` |

Resposta `200` (array; pode ser vazio):

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

O gabarito **não** é retornado na listagem.

#### Enviar resposta

`POST /quiz/{id}/responder`

Corpo:

```json
{
  "apelido": "ana",
  "resposta": "B"
}
```

`resposta` deve ser uma das letras `A`, `B`, `C` ou `D`; maiúsculas e minúsculas são aceitas. `apelido` é obrigatório, tem espaços removidos nas pontas e deve conter de 1 a 30 caracteres.

Resposta `200`:

```json
{
  "correta": true,
  "resposta_certa": "B",
  "explicacao": "O sujeito é o termo sobre o qual se declara algo.",
  "pontos_totais": 20
}
```

Pontuação por acerto: fácil `10`, médio `20`, difícil `30`. Respostas incorretas não adicionam pontos, mas atualizam a estatística de erros.

### 3.3 Flashcards

#### Buscar flashcards

`GET /flashcards/?tema=morfologia&limite=10`

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `tema` | string | Filtro opcional pelo tema |
| `limite` | inteiro | Quantidade desejada; padrão `10`, máximo `30` |

Resposta `200`:

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

A resposta contém frente e verso. A interface deve controlar a revelação do verso, por exemplo mostrando primeiro `frente`.

#### Registrar revisão

`POST /flashcards/{id}/revisar`

Corpo:

```json
{
  "apelido": "ana",
  "sabia": true
}
```

`sabia` é obrigatório e deve ser um booleano JSON literal (`true` ou `false`), não uma string.

Resposta `200`:

```json
{
  "sabia": true,
  "pontos_totais": 5
}
```

Marcar `sabia: true` adiciona 5 pontos e conta como acerto. `sabia: false` não adiciona pontos e conta como erro.

### 3.4 Completar lacunas

#### Buscar exercícios

`GET /lacunas/?tema=sintaxe&limite=5`

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `tema` | string | Filtro opcional pelo tema |
| `limite` | inteiro | Quantidade desejada; padrão `5`, máximo `30` |

Resposta `200`:

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

O gabarito não é retornado na listagem. `opcoes` é um array de strings.

#### Enviar resposta

`POST /lacunas/{id}/responder`

Corpo:

```json
{
  "apelido": "ana",
  "resposta": "a"
}
```

`resposta` deve ser texto não vazio. A API compara a resposta sem diferenciar maiúsculas e minúsculas.

Resposta `200`:

```json
{
  "correta": true,
  "resposta_certa": "a",
  "explicacao": "O verbo 'chegar' pede a preposição 'a'.",
  "pontos_totais": 15
}
```

Resposta correta adiciona 15 pontos; resposta incorreta não adiciona pontos e conta como erro.

### 3.5 Ranking

`GET /ranking`

Sem parâmetros ou corpo. Retorna até 10 jogadores, ordenados por pontos decrescentes e, em caso de empate, por apelido.

Resposta `200`:

```json
[
  {
    "apelido": "ana",
    "pontos": 120
  },
  {
    "apelido": "bia",
    "pontos": 95
  }
]
```

Se ainda não houver jogadores, retorna `[]`.

### 3.6 Perfil e estatísticas do jogador

`GET /jogadores/{apelido}`

Sem corpo. Codifique o apelido como segmento de URL ao montar o caminho (por exemplo, com `encodeURIComponent` no JavaScript).

Resposta `200` para jogador existente:

```json
{
  "apelido": "ana",
  "pontos": 120,
  "acertos": 8,
  "erros": 3
}
```

Para apelido inexistente, a API responde `200` com valores zerados e **não** cria o jogador:

```json
{
  "apelido": "novo_jogador",
  "pontos": 0,
  "acertos": 0,
  "erros": 0
}
```

## 4. Erros e tratamento no cliente

Erros retornados pela API usam JSON no formato:

```json
{
  "erro": "Descrição do erro."
}
```

| Status | Significado | Ação sugerida no front-end |
|---|---|---|
| `200` | Requisição processada | Consumir o JSON da resposta |
| `400` | Corpo JSON ausente/malformado ou campos inválidos | Mostrar mensagem de validação e permitir corrigir |
| `404` | ID de questão, flashcard ou lacuna não encontrado | Atualizar a atividade ou informar que ela não está mais disponível |
| `500` | Erro interno do servidor | Mostrar mensagem genérica e permitir tentar novamente |

O perfil de jogador inexistente não é um `404`; ele retorna `200` com estatísticas zeradas. Mensagens específicas de `400` e `404` dependem da rota. Erros de rede (servidor indisponível ou falha de conexão) não são respostas HTTP e precisam de tratamento separado no cliente.

## 5. Exemplo de integração com `fetch`

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5000";

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.erro ?? `Falha na API (${response.status})`);
  }

  return data;
}

async function carregarQuiz() {
  return apiFetch("/quiz/?tema=sintaxe&nivel=facil&limite=5");
}

async function responderQuiz(questaoId, apelido, alternativa) {
  return apiFetch(`/quiz/${questaoId}/responder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ apelido, resposta: alternativa }),
  });
}

async function carregarPerfil(apelido) {
  return apiFetch(`/jogadores/${encodeURIComponent(apelido)}`);
}
```

Use o `id` recebido na listagem para enviar a resposta. Após uma resposta ou revisão bem-sucedida, atualize no estado da interface o resultado e `pontos_totais`; o perfil e o ranking podem ser buscados novamente quando for necessário sincronizar as estatísticas.
