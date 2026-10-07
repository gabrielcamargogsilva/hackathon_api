CREATE TABLE IF NOT EXISTS questoes (
    id          SERIAL PRIMARY KEY,
    tema        TEXT NOT NULL,
    nivel       TEXT NOT NULL CHECK (nivel IN ('facil', 'medio', 'dificil')),
    pergunta    TEXT NOT NULL,
    alt_a       TEXT NOT NULL,
    alt_b       TEXT NOT NULL,
    alt_c       TEXT NOT NULL,
    alt_d       TEXT NOT NULL,
    resposta    CHAR(1) NOT NULL CHECK (resposta IN ('A', 'B', 'C', 'D')),
    explicacao  TEXT
);

CREATE TABLE IF NOT EXISTS flashcards (
    id      SERIAL PRIMARY KEY,
    tema    TEXT NOT NULL,
    frente  TEXT NOT NULL,
    verso   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lacunas (
    id          SERIAL PRIMARY KEY,
    tema        TEXT NOT NULL,
    frase       TEXT NOT NULL,          -- "Ele chegou ___ casa cedo."
    opcoes      JSONB NOT NULL,         -- ["em", "a", "na"]
    resposta    TEXT NOT NULL,
    explicacao  TEXT
);

CREATE TABLE IF NOT EXISTS jogadores (
    apelido  TEXT PRIMARY KEY,
    pontos   INTEGER NOT NULL DEFAULT 0,
    acertos  INTEGER NOT NULL DEFAULT 0,
    erros    INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_questoes_tema_nivel ON questoes (tema, nivel);
CREATE INDEX IF NOT EXISTS idx_flashcards_tema ON flashcards (tema);
CREATE INDEX IF NOT EXISTS idx_lacunas_tema ON lacunas (tema);
CREATE INDEX IF NOT EXISTS idx_jogadores_pontos ON jogadores (pontos DESC);
