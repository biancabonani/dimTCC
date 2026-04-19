import sqlite3

def criar_banco():
    conexao = sqlite3.connect("dim.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()

    print("Banco criado com sucesso!")

if __name__ == "__main__":
    criar_banco()