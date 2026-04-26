from flask import Flask, render_template, request, redirect, url_for, session
import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# armazenamento temporário
codes_db = {}

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


def generate_code():
    return str(random.randint(100000, 999999))


def send_email(to_email, code):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "[SOC] Código de verificação"

    body = f"""
Olá,

Seu código de verificação é: {code}

Se não foi você, ignore este e-mail.

--
Security Operations Center
"""

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"[OK] E-mail enviado para {to_email}")

    except Exception as e:
        print("[ERRO] Falha ao enviar e-mail:", e)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")

        if email:
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
            return "Código validado com sucesso!"
        else:
            return render_template("verify.html", error="Código inválido!")

    return render_template("verify.html")


@app.route("/resend")
def resend():
    email = session.get("email")

    if email:
        code = generate_code()
        codes_db[email] = code
        send_email(email, code)

    return redirect(url_for("verify"))


if __name__ == "__main__":
    app.run(debug=True)