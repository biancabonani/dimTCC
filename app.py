from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key="dim123"


def get_db():

    conexao=sqlite3.connect("dim.db")
    return conexao


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form.get("email")
        senha=request.form.get("senha")

        conexao=get_db()
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


@app.route("/cadastro",methods=["GET","POST"])
def cadastro():

    if request.method=="POST":

        nome=request.form.get("nome")
        email=request.form.get("email")
        senha=request.form.get("senha")

        conexao=get_db()
        cursor=conexao.cursor()

        cursor.execute("""

        INSERT INTO usuarios(
        nome,
        email,
        senha
        )

        VALUES(?,?,?)

        """,(nome,email,senha))

        conexao.commit()
        conexao.close()

        return redirect("/login")

    return render_template("cadastro.html")


@app.route("/dashboard",methods=["GET","POST"])
def dashboard():

    if "usuario_id" not in session:
        return redirect("/login")

    conexao=get_db()
    cursor=conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mensagem TEXT
    )
    """)


    if request.method=="POST":

        tarefa=request.form.get("tarefa")
        prioridade=request.form.get("prioridade")
        prazo=request.form.get("prazo")
        responsavel=request.form.get("responsavel")

        cursor.execute("""

        INSERT INTO tarefas(
        tarefa,
        usuario_id,
        prioridade,
        prazo,
        responsavel
        )

        VALUES(?,?,?,?,?)

        """,(

        tarefa,
        session["usuario_id"],
        prioridade,
        prazo,
        responsavel

        ))

        cursor.execute("""

        INSERT INTO historico(
        mensagem
        )

        VALUES(?)

        """,(

        f'{session["nome"]} criou "{tarefa}"',

        ))

        conexao.commit()


    busca=request.args.get("busca","")

    cursor.execute("""

    SELECT *
    FROM tarefas
    WHERE usuario_id=?

    """,(session["usuario_id"],))

    tarefas=cursor.fetchall()


    if busca:

        tarefas=[

        t for t in tarefas

        if busca.lower() in str(t[1]).lower()
        or busca.lower() in str(t[6]).lower()

        ]


    tarefas_novas=[]

    hoje=date.today()

    for tarefa in tarefas:

        tarefa=list(tarefa)

        atrasada=False
        proximo=False

        if tarefa[5]:

            try:

                prazo=datetime.strptime(
                tarefa[5],
                "%Y-%m-%d"
                ).date()

                if prazo<hoje and tarefa[2]!="Concluído":

                    atrasada=True

                elif hoje<=prazo<=hoje+timedelta(days=2):

                    proximo=True

            except:
                pass


        tarefa.append(atrasada)
        tarefa.append(proximo)

        tarefas_novas.append(tarefa)


    tarefas=tarefas_novas


    total=len(tarefas)
    fazer=len([t for t in tarefas if t[2]=="A Fazer"])
    andamento=len([t for t in tarefas if t[2]=="Em Andamento"])
    concluido=len([t for t in tarefas if t[2]=="Concluído"])


    cursor.execute("""

    SELECT *
    FROM historico
    ORDER BY id DESC
    LIMIT 8

    """)

    historico=cursor.fetchall()

    conexao.close()

    return render_template(

    "dashboard.html",

    tarefas=tarefas,
    historico=historico,
    busca=busca,
    total=total,
    fazer=fazer,
    andamento=andamento,
    concluido=concluido

    )


@app.route("/mudar/<int:id>/<status>")
def mudar(id,status):

    conexao=get_db()
    cursor=conexao.cursor()

    cursor.execute("""

    SELECT tarefa
    FROM tarefas
    WHERE id=?

    """,(id,))

    tarefa=cursor.fetchone()

    cursor.execute("""

    UPDATE tarefas
    SET status=?
    WHERE id=?

    """,(status,id))


    if tarefa:

        cursor.execute("""

        INSERT INTO historico(
        mensagem
        )

        VALUES(?)

        """,(

        f'{session["nome"]} moveu "{tarefa[0]}" para {status}',

        ))


    conexao.commit()
    conexao.close()

    return redirect("/dashboard")


@app.route("/excluir/<int:id>")
def excluir(id):

    conexao=get_db()
    cursor=conexao.cursor()

    cursor.execute("""

    SELECT tarefa
    FROM tarefas
    WHERE id=?

    """,(id,))

    tarefa=cursor.fetchone()


    if tarefa:

        cursor.execute("""

        INSERT INTO historico(
        mensagem
        )

        VALUES(?)

        """,(

        f'{session["nome"]} excluiu "{tarefa[0]}"',

        ))


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