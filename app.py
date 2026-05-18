from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key="dim123"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form.get("email")
        senha=request.form.get("senha")

        conexao=sqlite3.connect("dim.db")
        cursor=conexao.cursor()

        cursor.execute("""
        SELECT id,nome,email
        FROM usuarios
        WHERE email=? AND senha=?
        """,(email,senha))

        usuario=cursor.fetchone()

        conexao.close()

        if usuario:

            session["usuario_id"]=usuario[0]
            session["nome"]=usuario[1]

            return redirect("/dashboard")

        return "Email ou senha inválidos"

    return render_template("login.html")


@app.route("/cadastro", methods=["GET","POST"])
def cadastro():

    if request.method=="POST":

        nome=request.form.get("nome")
        email=request.form.get("email")
        senha=request.form.get("senha")

        conexao=sqlite3.connect("dim.db")
        cursor=conexao.cursor()

        cursor.execute("""
        INSERT INTO usuarios(nome,email,senha)
        VALUES(?,?,?)
        """,(nome,email,senha))

        conexao.commit()
        conexao.close()

        return redirect("/login")

    return render_template("cadastro.html")


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if "usuario_id" not in session:
        return redirect("/login")

    conexao=sqlite3.connect("dim.db")
    cursor=conexao.cursor()

    try:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN usuario_id INTEGER
        """)
    except:
        pass

    try:
        cursor.execute("""
        ALTER TABLE tarefas
        ADD COLUMN status TEXT DEFAULT 'A Fazer'
        """)
    except:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarefa TEXT,
        status TEXT DEFAULT 'A Fazer',
        usuario_id INTEGER
    )
    """)

    if request.method=="POST":

        tarefa=request.form.get("tarefa")

        if tarefa:

            cursor.execute("""
            INSERT INTO tarefas(
            tarefa,
            usuario_id
            )
            VALUES(?,?)
            """,(tarefa,session["usuario_id"]))

            conexao.commit()

    cursor.execute("""
    SELECT *
    FROM tarefas
    WHERE usuario_id=?
    """,(session["usuario_id"],))

    tarefas=cursor.fetchall()

    total=len(tarefas)
    fazer=len([t for t in tarefas if t[2]=="A Fazer"])
    andamento=len([t for t in tarefas if t[2]=="Em Andamento"])
    concluido=len([t for t in tarefas if t[2]=="Concluído"])

    conexao.close()

    return render_template(
        "dashboard.html",
        tarefas=tarefas,
        total=total,
        fazer=fazer,
        andamento=andamento,
        concluido=concluido
    )


@app.route("/mudar/<int:id>/<status>")
def mudar(id,status):

    conexao=sqlite3.connect("dim.db")
    cursor=conexao.cursor()

    cursor.execute("""
    UPDATE tarefas
    SET status=?
    WHERE id=?
    """,(status,id))

    conexao.commit()
    conexao.close()

    return redirect("/dashboard")


@app.route("/excluir/<int:id>")
def excluir(id):

    conexao=sqlite3.connect("dim.db")
    cursor=conexao.cursor()

    cursor.execute("""
    DELETE FROM tarefas
    WHERE id=?
    """,(id,))

    conexao.commit()
    conexao.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__=="__main__":
    app.run(debug=True)