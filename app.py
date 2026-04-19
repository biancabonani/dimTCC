from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conexao = sqlite3.connect("dim.db")
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT * FROM usuarios
            WHERE email = ? AND senha = ?
        """, (email, senha))

        usuario = cursor.fetchone()
        conexao.close()

        if usuario:
            return "Login realizado com sucesso!"
        else:
            return "Email ou senha inválidos!"

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        conexao = sqlite3.connect("dim.db")
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        """, (nome, email, senha))

        conexao.commit()
        conexao.close()

        return "Usuário cadastrado com sucesso!"

    return render_template("cadastro.html")


if __name__ == "__main__":
    app.run(debug=True)