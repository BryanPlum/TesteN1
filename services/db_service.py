from openpyxl import Workbook, load_workbook
import os


DB_FILE = "data/db.xlsx"


def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(DB_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Users"
        ws.append(["Usuario", "Senha"])
        wb.save(DB_FILE)


def save_user(email, password):
    wb = load_workbook(DB_FILE)
    ws = wb.active
    ws.append([email, password])
    wb.save(DB_FILE)

init_db()

def get_user(email):
    wb = load_workbook(DB_FILE)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):
        user_email, user_password = row
        if user_email == email:
            return user_password

    return None