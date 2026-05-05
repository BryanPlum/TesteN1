from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os

from services.email_service import send_email
from services.auth_service import generate_code, validate_password, hash_password, check_password
from services.db_service import init_db, save_user, get_user

app = Flask(__name__)
app.secret_key = "supersecretkey"

codes_db = {}

init_db()

#________ROTA DEFAULT__________
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")

        code = generate_code()
        codes_db[email] = code

        send_email(email, code)

        session["email"] = email

        return redirect(url_for("verify"))

    return render_template("index.html")

#________________ROTA DE VERIFICAÇÃO DO CÓDIGO_________________
@app.route("/verify", methods=["GET", "POST"])
def verify():
    email = session.get("email")

    if request.method == "POST":
        user_code = request.form.get("code")

        if codes_db.get(email) == user_code:
            return redirect(url_for("create_password"))

        return render_template("verify.html", error="Código inválido")

    return render_template("verify.html")

#_______________ROTA DE CRIAÇÃO DE SENHA_________________
@app.route("/create-password", methods=["GET", "POST"])

def create_password():
    email = session.get("email")

    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        error = validate_password(password)

        if error:
            return render_template("create_password.html", error=error)

        if password != confirm:
            return render_template("create_password.html", error="Senhas não coincidem")

        hashed = hash_password(password)
        save_user(email, hashed)

        return redirect(url_for("login"))
        
    return render_template("create_password.html")
    

#_____________ROTA DE LOGIN________________________________
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        stored_password = get_user(email)

        if not stored_password:
            return render_template("login.html", error="Usuário não encontrado")

        if not check_password(password, stored_password):
            return render_template("login.html", error="Senha inválida")

        session["user"] = email

        # redireciona para o dashboard
        return redirect(url_for("dashboard"))

    return render_template("login.html")

#_______ROTA DE REENVIO DE CÓDIGO PARA EMAIL_____________________
@app.route("/resend")
def resend():
    email = session.get("email")

    if email:
        code = generate_code()
        codes_db[email] = code
        send_email(email, code)

    return redirect(url_for("verify"))

#________ROTA DE REDEFINIÇÃO DE SENHA____________________________
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        # verificar se usuário existe
        from services.db_service import get_user
        if not get_user(email):
            return render_template("forgot_password.html", error="Usuário não encontrado")

        code = generate_code()
        codes_db[email] = code

        send_email(email, code)

        session["reset_email"] = email

        return redirect(url_for("reset_verify"))

    return render_template("forgot_password.html")

#______________ROTA PARA VALIDAR CÓDIGO DE REDEFINIÇÃO DE SENHA__
@app.route("/reset-verify", methods=["GET", "POST"])
def reset_verify():
    email = session.get("reset_email")

    if request.method == "POST":
        code = request.form.get("code")

        if codes_db.get(email) == code:
            return redirect(url_for("reset_password"))

        return render_template("reset_verify.html", error="Código inválido")

    return render_template("reset_verify.html")

#__________ROTA PARA FORMULÁRIO DE REDEFINIR SENHA___
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")

    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        error = validate_password(password)

        if error:
            return render_template("create_password.html", error=error)

        if password != confirm:
            return render_template("create_password.html", error="Senhas não coincidem")

        hashed = hash_password(password)

        from services.db_service import update_password
        update_password(email, hashed)

        return redirect(url_for("login"))

    return render_template("create_password.html")

#______ROTA DASHBOARD__________
@app.route("/dashboard")
def dashboard():
    user = session.get("user")

    if not user:
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)

#______ROTA LOGOUT______________
@app.route("/logout")
def logout():
    session.clear()  # remove tudo da sessão
    return redirect(url_for("login"))


#______ROTA DOS CASOS____________
@app.route("/case1", methods=["GET", "POST"])
def case1():
    user = session.get("user")

    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        answer1 = request.form.get("answer1")
        answer2 = request.form.get("answer2")

        if not answer1 or not answer2:
            return render_template("case1.html", user=user, error="Selecione todas as respostas")

        from services.db_service import save_case1_answers
        save_case1_answers(user, answer1, answer2)

        return render_template("case1.html", user=user, success="Respostas enviadas com sucesso!")

    return render_template("case1.html", user=user)

    return render_template("case1.html", user=user)


@app.route("/case2")
def case2():
    return "Caso 2 em construção"

@app.route("/case3")
def case3():
    user = session.get("user")

    if not user:
        return redirect(url_for("login"))

    return render_template("case3.html", user=user)

#______LINK DE ARQUIVOS NA PASTA RESOURCES______
@app.route("/resources/<path:filename>")
def serve_resource(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "resources", filename)

    return send_file(file_path)

if __name__ == "__main__":
    app.run(debug=True)