from flask import Flask, render_template, request, redirect, url_for, session

from services.email_service import send_email
from services.auth_service import generate_code, validate_password, hash_password, check_password
from services.db_service import init_db, save_user, get_user

app = Flask(__name__)
app.secret_key = "supersecretkey"

codes_db = {}

init_db()


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


@app.route("/verify", methods=["GET", "POST"])
def verify():
    email = session.get("email")

    if request.method == "POST":
        user_code = request.form.get("code")

        if codes_db.get(email) == user_code:
            return redirect(url_for("create_password"))

        return render_template("verify.html", error="Código inválido")

    return render_template("verify.html")


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

        return "Login realizado com sucesso! (próxima etapa: incidente)"

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)