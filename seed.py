"""Cria as tabelas e popula o conteúdo. Pode rodar de novo: limpa o conteúdo
(questões, flashcards, lacunas) e preserva os jogadores."""
from psycopg2.extras import Json
from app import app
from db import init_db, get_conn

# (tema, nivel, pergunta, A, B, C, D, resposta, explicacao)
QUESTOES = [
    ("sintaxe", "facil", "Qual é o sujeito em 'Os alunos chegaram cedo à escola'?",
     "Os alunos", "cedo", "à escola", "chegaram", "A",
     "O sujeito é o termo sobre o qual se declara algo; aqui, quem chegou: 'Os alunos'."),
    ("sintaxe", "medio", "Em 'Maria entregou o livro ao professor', qual é o objeto indireto?",
     "o livro", "ao professor", "Maria", "entregou", "B",
     "O objeto indireto completa o verbo com preposição: 'ao professor' (a + o professor)."),
    ("sintaxe", "medio", "Qual frase está de acordo com a norma-padrão?",
     "Fazem dois anos que moro aqui.", "Faz dois anos que moro aqui.",
     "Haviam muitas pessoas na sala.", "Existe muitas pessoas na sala.", "B",
     "O verbo 'fazer' indicando tempo decorrido é impessoal e fica na 3ª pessoa do singular."),
    ("sintaxe", "dificil", "Em 'Precisa-se de professores', o sujeito é:",
     "professores", "oculto", "indeterminado", "inexistente", "C",
     "O verbo é transitivo indireto e o 'se' é índice de indeterminação do sujeito."),
    ("morfologia", "facil", "Qual é o prefixo da palavra 'infeliz'?",
     "-feliz", "fel-", "infe-", "in-", "D",
     "O prefixo é o afixo que vem antes do radical: in- + feliz."),
    ("morfologia", "facil", "Qual é o radical da palavra 'pedreiro'?",
     "pedr-", "-eiro", "pedre", "ped", "A",
     "Pedreiro = pedr(a) + -eiro. O radical carrega o significado básico; -eiro é sufixo."),
    ("morfologia", "medio", "Qual processo de formação originou 'guarda-chuva'?",
     "derivação prefixal", "composição por justaposição", "parassíntese", "hibridismo", "B",
     "Duas palavras se unem sem perder sua integridade fonética: justaposição."),
    ("morfologia", "dificil", "A palavra 'entardecer' foi formada por:",
     "derivação sufixal", "derivação prefixal", "parassíntese", "composição por aglutinação", "C",
     "Prefixo en- e sufixo -ecer foram acrescentados ao mesmo tempo ao radical 'tard-'."),
    ("pragmatica", "facil", "Qual palavra é um exemplo de dêixis de lugar?",
     "ontem", "nós", "aqui", "mesmo", "C",
     "'Aqui' só tem sentido em relação ao local de quem fala."),
    ("pragmatica", "medio",
     "Ao dizer 'Que frio!' perto de uma janela aberta, pedindo que a fechem, ocorre:",
     "ato de fala indireto", "pleonasmo", "pressuposição", "polissemia", "A",
     "O falante realiza um pedido sem usar uma forma imperativa direta."),
    ("pragmatica", "medio", "Em 'Ele parou de fumar', pressupõe-se que:",
     "ele nunca fumou", "ele fumava antes", "ele vai voltar a fumar", "ele fuma pouco", "B",
     "O verbo 'parar de' pressupõe que a ação acontecia anteriormente."),
    ("pragmatica", "dificil",
     "Ao dizer 'Você é muito pontual!' a quem chegou uma hora atrasado, o falante usa:",
     "metáfora", "eufemismo", "ironia", "pleonasmo", "C",
     "Na ironia, o sentido pretendido é o oposto do que foi literalmente dito."),
    ("revisao_geral", "facil", "Em qual frase a crase está usada corretamente?",
     "Fui à pé até lá.", "Vou à escola.", "Disse à ele a verdade.", "Estou disposto à ajudar.", "B",
     "Há fusão da preposição 'a' com o artigo 'a' de 'escola'. Não se usa crase antes de verbo, "
     "de pronome pessoal ou de palavra masculina."),
]

# (tema, frente, verso)
FLASHCARDS = [
    ("morfologia", "O que é radical?", "Parte da palavra que carrega o significado básico (ex.: pedr- em pedreiro)."),
    ("morfologia", "O que é prefixo?", "Afixo colocado antes do radical (ex.: in-feliz)."),
    ("morfologia", "O que é sufixo?", "Afixo colocado depois do radical (ex.: feliz-mente)."),
    ("morfologia", "O que é vogal temática?", "Vogal que liga o radical às desinências (ex.: o 'a' de cantar)."),
    ("morfologia", "O que é desinência?", "Terminação que indica flexão de gênero, número, pessoa, modo ou tempo."),
    ("sintaxe", "O que é sujeito?", "Termo sobre o qual se declara algo; concorda com o verbo."),
    ("sintaxe", "O que é predicado?", "Tudo o que se declara sobre o sujeito."),
    ("sintaxe", "Objeto direto x indireto?", "O direto completa o verbo sem preposição; o indireto, com preposição."),
    ("sintaxe", "O que é sujeito indeterminado?", "Quando não se quer ou não se pode identificar o sujeito (ex.: Roubaram o carro)."),
    ("pragmatica", "O que é implicatura?", "Sentido subentendido que vai além do que foi dito literalmente."),
    ("pragmatica", "O que é dêixis?", "Uso de palavras cujo sentido depende do contexto (eu, aqui, agora)."),
    ("pragmatica", "O que é ato de fala indireto?", "Realizar uma ação (pedido, ordem) usando uma forma que não é a esperada."),
    ("pragmatica", "O que é pressuposição?", "Informação tida como certa pelo enunciado (ex.: 'parou de fumar' pressupõe que fumava)."),
]

# (tema, frase, opcoes, resposta, explicacao)
LACUNAS = [
    ("sintaxe", "Ele chegou ___ casa cedo.", ["em", "a", "na"], "a",
     "O verbo 'chegar' pede a preposição 'a' (chegar a algum lugar)."),
    ("sintaxe", "___ dois anos que não o vejo.", ["Fazem", "Faz", "Fazendo"], "Faz",
     "O verbo 'fazer' indicando tempo é impessoal: fica no singular."),
    ("sintaxe", "Prefiro cinema ___ teatro.", ["do que", "a", "que"], "a",
     "O verbo 'preferir' rege a preposição 'a'."),
    ("sintaxe", "Assisti ___ filme ontem.", ["o", "ao", "no"], "ao",
     "No sentido de 'ver', 'assistir' é transitivo indireto e pede 'a'."),
    ("sintaxe", "Ela é a mulher ___ filho estudou comigo.", ["que", "cujo", "onde"], "cujo",
     "'Cujo' é pronome relativo que indica posse e concorda com o termo seguinte."),
    ("sintaxe", "Ontem os alunos ___ a prova.", ["fez", "fizeram"], "fizeram",
     "O verbo concorda com o sujeito plural 'os alunos'."),
    ("revisao_geral", "Obedeça ___ regras.", ["as", "às"], "às",
     "'Obedecer' pede a preposição 'a', que se funde com o artigo: às."),
    ("revisao_geral", "Ele se esqueceu ___ tarefa.", ["da", "a", "na"], "da",
     "'Esquecer-se' rege a preposição 'de': de + a = da."),
]

with app.app_context():
    init_db()
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE questoes, flashcards, lacunas RESTART IDENTITY")
        cur.executemany(
            "INSERT INTO questoes (tema, nivel, pergunta, alt_a, alt_b, alt_c, alt_d, resposta, explicacao) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", QUESTOES)
        cur.executemany(
            "INSERT INTO flashcards (tema, frente, verso) VALUES (%s,%s,%s)", FLASHCARDS)
        cur.executemany(
            "INSERT INTO lacunas (tema, frase, opcoes, resposta, explicacao) VALUES (%s,%s,%s,%s,%s)",
            [(t, f, Json(o), r, e) for t, f, o, r, e in LACUNAS])
    conn.commit()
    print(f"Seed ok: {len(QUESTOES)} questões, {len(FLASHCARDS)} flashcards, {len(LACUNAS)} lacunas.")
