import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


# carregar variáveis de ambiente
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


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