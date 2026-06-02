import sqlite3


def criar_banco():

    conexao = sqlite3.connect("dim.db")
    cursor = conexao.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projetos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        gerente_id INTEGER NOT NULL,
        FOREIGN KEY(gerente_id) REFERENCES usuarios(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarefa TEXT NOT NULL,
        status TEXT DEFAULT 'A Fazer',
        usuario_id INTEGER,
        projeto_id INTEGER,
        prioridade TEXT DEFAULT 'Média',
        prazo TEXT,
        responsavel TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(projeto_id) REFERENCES projetos(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mensagem TEXT NOT NULL
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projeto_membros(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projeto_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        papel TEXT DEFAULT 'Membro',
        FOREIGN KEY(projeto_id) REFERENCES projetos(id),
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)


    conexao.commit()
    conexao.close()

    print("Banco de dados criado/atualizado com sucesso!")


def verificar_colunas():

    conexao = sqlite3.connect("dim.db")
    cursor = conexao.cursor()


    cursor.execute("PRAGMA table_info(tarefas)")
    colunas_tarefas = [coluna[1] for coluna in cursor.fetchall()]


    if "status" not in colunas_tarefas:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN status TEXT DEFAULT 'A Fazer'
        """)


    if "usuario_id" not in colunas_tarefas:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN usuario_id INTEGER
        """)


    if "projeto_id" not in colunas_tarefas:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN projeto_id INTEGER
        """)


    if "prioridade" not in colunas_tarefas:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN prioridade TEXT DEFAULT 'Média'
        """)


    if "prazo" not in colunas_tarefas:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN prazo TEXT
        """)


    if "responsavel" not in colunas_tarefas:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN responsavel TEXT
        """)


    conexao.commit()
    conexao.close()

    print("Estrutura das tabelas verificada com sucesso!")


if __name__ == "__main__":

    criar_banco()
    verificar_colunas()