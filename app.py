from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "dim123"


def get_db():

    conexao = sqlite3.connect("dim.db")
    return conexao


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        conexao = get_db()
        cursor = conexao.cursor()

        cursor.execute("""
        SELECT id, nome, email
        FROM usuarios
        WHERE email=? AND senha=?
        """, (email, senha))

        usuario = cursor.fetchone()

        conexao.close()

        if usuario:

            session["usuario_id"] = usuario[0]
            session["nome"] = usuario[1]

            return redirect("/dashboard")

        return "Email ou senha inválidos"

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        conexao = get_db()
        cursor = conexao.cursor()

        cursor.execute("""
        INSERT INTO usuarios(
            nome,
            email,
            senha
        )
        VALUES(?,?,?)
        """, (nome, email, senha))

        conexao.commit()
        conexao.close()

        return redirect("/login")

    return render_template("cadastro.html")


@app.route("/projetos", methods=["GET", "POST"])
def projetos():

    if "usuario_id" not in session:
        return redirect("/login")

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projetos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        gerente_id INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projeto_membros(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projeto_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        papel TEXT DEFAULT 'Membro'
    )
    """)

    if request.method == "POST":

        nome = request.form.get("nome")
        descricao = request.form.get("descricao")

        if nome:

            cursor.execute("""
            INSERT INTO projetos(
                nome,
                descricao,
                gerente_id
            )
            VALUES(?,?,?)
            """, (
                nome,
                descricao,
                session["usuario_id"]
            ))

            projeto_id = cursor.lastrowid

            cursor.execute("""
            INSERT INTO projeto_membros(
                projeto_id,
                usuario_id,
                papel
            )
            VALUES(?,?,?)
            """, (
                projeto_id,
                session["usuario_id"],
                "Gerente"
            ))

            cursor.execute("""
            INSERT INTO historico(
                mensagem
            )
            VALUES(?)
            """, (
                f'{session["nome"]} criou o projeto "{nome}"',
            ))

            conexao.commit()

    cursor.execute("""
    SELECT DISTINCT
        projetos.id,
        projetos.nome,
        projetos.descricao,
        projetos.gerente_id
    FROM projetos
    LEFT JOIN projeto_membros
    ON projetos.id = projeto_membros.projeto_id
    WHERE projetos.gerente_id=?
    OR projeto_membros.usuario_id=?
    ORDER BY projetos.id DESC
    """, (
        session["usuario_id"],
        session["usuario_id"]
    ))

    projetos = cursor.fetchall()

    conexao.close()

    return render_template(
        "projetos.html",
        projetos=projetos
    )


@app.route("/selecionar_projeto/<int:id>")
def selecionar_projeto(id):

    if "usuario_id" not in session:
        return redirect("/login")

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT id, nome
    FROM projetos
    WHERE id=?
    AND gerente_id=?
    """, (
        id,
        session["usuario_id"]
    ))

    projeto = cursor.fetchone()

    if projeto:

        session["projeto_id"] = projeto[0]
        session["projeto_nome"] = projeto[1]

    conexao.close()

    return redirect("/dashboard")


@app.route("/limpar_projeto")
def limpar_projeto():

    session.pop("projeto_id", None)
    session.pop("projeto_nome", None)

    return redirect("/dashboard")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "usuario_id" not in session:
        return redirect("/login")

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mensagem TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projetos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        gerente_id INTEGER NOT NULL
    )
    """)

    projeto_id = session.get("projeto_id")
    projeto_nome = session.get("projeto_nome")

    if request.method == "POST":

        tarefa = request.form.get("tarefa")
        prioridade = request.form.get("prioridade")
        prazo = request.form.get("prazo")
        responsavel = request.form.get("responsavel")

        if tarefa:

            cursor.execute("""
            INSERT INTO tarefas(
                tarefa,
                usuario_id,
                projeto_id,
                prioridade,
                prazo,
                responsavel
            )
            VALUES(?,?,?,?,?,?)
            """, (
                tarefa,
                session["usuario_id"],
                projeto_id,
                prioridade,
                prazo,
                responsavel
            ))

            if projeto_nome:

                mensagem = f'{session["nome"]} criou "{tarefa}" no projeto "{projeto_nome}"'

            else:

                mensagem = f'{session["nome"]} criou "{tarefa}"'

            cursor.execute("""
            INSERT INTO historico(
                mensagem
            )
            VALUES(?)
            """, (
                mensagem,
            ))

            conexao.commit()

    busca = request.args.get("busca", "")

    if projeto_id:

        cursor.execute("""
        SELECT
            id,
            tarefa,
            status,
            usuario_id,
            prioridade,
            prazo,
            responsavel
        FROM tarefas
        WHERE usuario_id=?
        AND projeto_id=?
        """, (
            session["usuario_id"],
            projeto_id
        ))

    else:

        cursor.execute("""
        SELECT
            id,
            tarefa,
            status,
            usuario_id,
            prioridade,
            prazo,
            responsavel
        FROM tarefas
        WHERE usuario_id=?
        """, (
            session["usuario_id"],
        ))

    tarefas = cursor.fetchall()

    if busca:

        tarefas = [

            t for t in tarefas

            if busca.lower() in str(t[1]).lower()
            or busca.lower() in str(t[6]).lower()
            or busca.lower() in str(t[4]).lower()
            or busca.lower() in str(t[2]).lower()

        ]

    tarefas_novas = []

    hoje = date.today()

    for tarefa in tarefas:

        tarefa = list(tarefa)

        atrasada = False
        proximo = False

        if tarefa[5]:

            try:

                prazo = datetime.strptime(
                    tarefa[5],
                    "%Y-%m-%d"
                ).date()

                if prazo < hoje and tarefa[2] != "Concluído":

                    atrasada = True

                elif hoje <= prazo <= hoje + timedelta(days=2):

                    proximo = True

            except:
                pass

        tarefa.append(atrasada)
        tarefa.append(proximo)

        tarefas_novas.append(tarefa)

    tarefas = tarefas_novas

    total = len(tarefas)
    fazer = len([t for t in tarefas if t[2] == "A Fazer"])
    andamento = len([t for t in tarefas if t[2] == "Em Andamento"])
    concluido = len([t for t in tarefas if t[2] == "Concluído"])

    cursor.execute("""
    SELECT *
    FROM historico
    ORDER BY id DESC
    LIMIT 8
    """)

    historico = cursor.fetchall()

    conexao.close()

    return render_template(
        "dashboard.html",
        tarefas=tarefas,
        historico=historico,
        busca=busca,
        total=total,
        fazer=fazer,
        andamento=andamento,
        concluido=concluido,
        projeto_nome=projeto_nome
    )


@app.route("/tarefas")
def tarefas():

    if "usuario_id" not in session:
        return redirect("/login")

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT
        tarefas.id,
        tarefas.tarefa,
        tarefas.status,
        tarefas.prioridade,
        tarefas.prazo,
        tarefas.responsavel,
        projetos.nome
    FROM tarefas
    LEFT JOIN projetos
    ON tarefas.projeto_id = projetos.id
    WHERE tarefas.usuario_id=?
    ORDER BY tarefas.id DESC
    """, (
        session["usuario_id"],
    ))

    tarefas = cursor.fetchall()

    conexao.close()

    return render_template(
        "tarefas.html",
        tarefas=tarefas
    )


@app.route("/notificacoes")
def notificacoes():

    if "usuario_id" not in session:
        return redirect("/login")

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT *
    FROM historico
    ORDER BY id DESC
    LIMIT 20
    """)

    notificacoes = cursor.fetchall()

    conexao.close()

    return render_template(
        "notificacoes.html",
        notificacoes=notificacoes
    )


@app.route("/perfil")
def perfil():

    if "usuario_id" not in session:
        return redirect("/login")

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT nome, email
    FROM usuarios
    WHERE id=?
    """, (
        session["usuario_id"],
    ))

    usuario = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*)
    FROM tarefas
    WHERE usuario_id=?
    """, (
        session["usuario_id"],
    ))

    total_tarefas = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM tarefas
    WHERE usuario_id=?
    AND status='Concluído'
    """, (
        session["usuario_id"],
    ))

    tarefas_concluidas = cursor.fetchone()[0]

    conexao.close()

    return render_template(
        "perfil.html",
        usuario=usuario,
        total_tarefas=total_tarefas,
        tarefas_concluidas=tarefas_concluidas
    )


@app.route("/mudar/<int:id>/<status>")
def mudar(id, status):

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT tarefa
    FROM tarefas
    WHERE id=?
    """, (
        id,
    ))

    tarefa = cursor.fetchone()

    cursor.execute("""
    UPDATE tarefas
    SET status=?
    WHERE id=?
    """, (
        status,
        id
    ))

    if tarefa:

        cursor.execute("""
        INSERT INTO historico(
            mensagem
        )
        VALUES(?)
        """, (
            f'{session["nome"]} moveu "{tarefa[0]}" para {status}',
        ))

    conexao.commit()
    conexao.close()

    return redirect("/dashboard")


@app.route("/excluir/<int:id>")
def excluir(id):

    conexao = get_db()
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT tarefa
    FROM tarefas
    WHERE id=?
    """, (
        id,
    ))

    tarefa = cursor.fetchone()

    if tarefa:

        cursor.execute("""
        INSERT INTO historico(
            mensagem
        )
        VALUES(?)
        """, (
            f'{session["nome"]} excluiu "{tarefa[0]}"',
        ))

    cursor.execute("""
    DELETE FROM tarefas
    WHERE id=?
    """, (
        id,
    ))

    conexao.commit()
    conexao.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)